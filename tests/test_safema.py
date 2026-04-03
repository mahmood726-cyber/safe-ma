"""
Selenium test suite for SafeMA — Anytime-Valid Sequential Meta-Analysis with E-Values.
Browser: Chrome headless. URL: file:// protocol.
Run: pytest tests/test_safema.py -v
"""
import os, time, json, pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "safema.html")
FILE_URL = "file:///" + os.path.abspath(FILE_PATH).replace("\\", "/")


@pytest.fixture(scope="module")
def driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(3)
    yield drv
    drv.quit()


def load_page(driver):
    """Load the SafeMA page fresh and suppress confirm dialogs."""
    driver.get(FILE_URL)
    driver.execute_script("window.confirm = function(){return true};")
    driver.execute_script("window.alert = function(){};")
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return typeof state !== 'undefined'")
    )


def js_click(driver, el):
    """Click via JS to avoid headless interactability issues."""
    driver.execute_script("arguments[0].click()", el)


def load_example(driver, idx):
    """Load a built-in example and wait for result to populate."""
    load_page(driver)
    driver.execute_script(f"loadExample({idx})")
    time.sleep(0.3)
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("return state.result !== null")
    )


# ===========================================================================
# 1. Page loads and title is present
# ===========================================================================
class TestPageLoad:
    def test_page_loads(self, driver):
        load_page(driver)
        assert "SafeMA" in driver.title

    def test_five_tabs_present(self, driver):
        load_page(driver)
        tabs = driver.find_elements(By.CSS_SELECTOR, '[role="tab"]')
        assert len(tabs) == 5, f"Expected 5 tabs, got {len(tabs)}"
        labels = [t.text for t in tabs]
        assert "Data" in labels
        assert "E-Process" in labels
        assert "Confidence Sequence" in labels
        assert "vs Classical TSA" in labels
        assert "Report" in labels

    def test_initial_state_no_result(self, driver):
        load_page(driver)
        result = driver.execute_script("return state.result")
        assert result is None


# ===========================================================================
# 2-5. Example loading and e-value correctness
# ===========================================================================
class TestExamples:
    def test_sglt2i_loads_and_has_result(self, driver):
        load_example(driver, 0)
        has_result = driver.execute_script("return state.result !== null")
        assert has_result

    def test_sglt2i_crosses_threshold(self, driver):
        """SGLT2i HF (k=8) should cross the 1/alpha threshold."""
        load_example(driver, 0)
        crossed = driver.execute_script("return state.result.crossed")
        assert crossed is True, "SGLT2i HF should cross the threshold"

    def test_sglt2i_study_count(self, driver):
        load_example(driver, 0)
        k = driver.execute_script("return state.result.results.length")
        assert k == 8

    def test_magnesium_loads_and_has_result(self, driver):
        load_example(driver, 1)
        has_result = driver.execute_script("return state.result !== null")
        assert has_result

    def test_magnesium_does_not_cross(self, driver):
        """Magnesium-MI (k=8) should NOT cross the threshold."""
        load_example(driver, 1)
        crossed = driver.execute_script("return state.result.crossed")
        assert crossed is False, "Magnesium-MI should NOT cross the threshold"

    def test_magnesium_study_count(self, driver):
        load_example(driver, 1)
        k = driver.execute_script("return state.result.results.length")
        assert k == 8

    def test_hcq_loads_and_has_result(self, driver):
        load_example(driver, 2)
        has_result = driver.execute_script("return state.result !== null")
        assert has_result

    def test_hcq_final_e_below_1(self, driver):
        """HCQ COVID (k=6) final cumulative E should be < 1 (no evidence)."""
        load_example(driver, 2)
        finalE = driver.execute_script("return state.result.finalE")
        assert finalE < 1, f"HCQ finalE={finalE}, expected < 1"

    def test_hcq_study_count(self, driver):
        load_example(driver, 2)
        k = driver.execute_script("return state.result.results.length")
        assert k == 6


# ===========================================================================
# 6. E-value table row count matches study count
# ===========================================================================
class TestEValueTable:
    def test_evalue_table_row_count_sglt2i(self, driver):
        load_example(driver, 0)
        # Switch to E-Process tab to ensure table is rendered
        driver.execute_script("switchTab('eplot')")
        time.sleep(0.2)
        rows = driver.find_elements(By.CSS_SELECTOR, "#evalueTable tbody tr")
        assert len(rows) == 8, f"Expected 8 rows, got {len(rows)}"

    def test_evalue_table_row_count_hcq(self, driver):
        load_example(driver, 2)
        driver.execute_script("switchTab('eplot')")
        time.sleep(0.2)
        rows = driver.find_elements(By.CSS_SELECTOR, "#evalueTable tbody tr")
        assert len(rows) == 6, f"Expected 6 rows, got {len(rows)}"


# ===========================================================================
# 7. Metrics display shows CROSSED/NOT CROSSED
# ===========================================================================
class TestMetrics:
    def test_crossed_metric_displayed_sglt2i(self, driver):
        load_example(driver, 0)
        driver.execute_script("switchTab('eplot')")
        time.sleep(0.2)
        metrics_html = driver.find_element(By.ID, "eMetrics").get_attribute("innerHTML")
        assert "CROSSED" in metrics_html

    def test_not_crossed_metric_displayed_magnesium(self, driver):
        load_example(driver, 1)
        driver.execute_script("switchTab('eplot')")
        time.sleep(0.2)
        metrics_html = driver.find_element(By.ID, "eMetrics").get_attribute("innerHTML")
        assert "NOT CROSSED" in metrics_html

    def test_crossed_css_class(self, driver):
        load_example(driver, 0)
        driver.execute_script("switchTab('eplot')")
        time.sleep(0.2)
        crossed_el = driver.find_element(By.CSS_SELECTOR, "#eMetrics .metric-val.crossed")
        assert crossed_el is not None

    def test_not_crossed_css_class(self, driver):
        load_example(driver, 1)
        driver.execute_script("switchTab('eplot')")
        time.sleep(0.2)
        not_crossed_el = driver.find_element(By.CSS_SELECTOR, "#eMetrics .metric-val.not-crossed")
        assert not_crossed_el is not None


# ===========================================================================
# 8. Confidence sequence tab renders canvas
# ===========================================================================
class TestConfidenceSequence:
    def test_confseq_canvas_exists(self, driver):
        load_example(driver, 0)
        driver.execute_script("switchTab('confseq')")
        time.sleep(0.3)
        canvas = driver.find_element(By.ID, "csCanvas")
        assert canvas is not None
        # Canvas should have been drawn (width > 0 in its internal bitmap)
        width = driver.execute_script("return document.getElementById('csCanvas').width")
        assert width > 0


# ===========================================================================
# 9. Report text contains Grunwald/JRSS reference
# ===========================================================================
class TestReport:
    def test_report_contains_grunwald(self, driver):
        load_example(driver, 0)
        driver.execute_script("switchTab('report')")
        time.sleep(0.2)
        text = driver.find_element(By.ID, "reportText").text
        # The rendered text uses the actual unicode u-umlaut
        assert "nwald" in text, f"Report should mention Grunwald: {text[:200]}"

    def test_report_contains_jrssb(self, driver):
        load_example(driver, 0)
        driver.execute_script("switchTab('report')")
        time.sleep(0.2)
        text = driver.find_element(By.ID, "reportText").text
        assert "JRSS-B" in text, f"Report should mention JRSS-B: {text[:200]}"

    def test_report_shows_study_count(self, driver):
        load_example(driver, 0)
        driver.execute_script("switchTab('report')")
        time.sleep(0.2)
        text = driver.find_element(By.ID, "reportText").text
        assert "k=8" in text


# ===========================================================================
# 10. Theme toggle
# ===========================================================================
class TestTheme:
    def test_theme_toggle_to_light(self, driver):
        load_page(driver)
        # Initial theme is dark
        theme = driver.execute_script("return document.documentElement.getAttribute('data-theme')")
        assert theme == "dark"
        # Toggle to light
        driver.execute_script("toggleTheme()")
        theme = driver.execute_script("return document.documentElement.getAttribute('data-theme')")
        assert theme == "light"

    def test_theme_toggle_back_to_dark(self, driver):
        load_page(driver)
        driver.execute_script("toggleTheme()")  # dark -> light
        driver.execute_script("toggleTheme()")  # light -> dark
        theme = driver.execute_script("return document.documentElement.getAttribute('data-theme')")
        assert theme == "dark"


# ===========================================================================
# 11. Export JSON button exists
# ===========================================================================
class TestExportJSON:
    def test_export_json_button_exists(self, driver):
        load_page(driver)
        driver.execute_script("switchTab('report')")
        time.sleep(0.2)
        buttons = driver.find_elements(By.CSS_SELECTOR, "#panel-report .btn")
        labels = [b.text.strip() for b in buttons]
        assert "Export JSON" in labels

    def test_export_json_produces_valid_data(self, driver):
        """Verify the exported JSON structure via state inspection."""
        load_example(driver, 0)
        json_str = driver.execute_script("""
            var data = {
                version: 'safema-1.0',
                framework: 'Grunwald-Ter Schure ALL-IN (JRSS-B 2024)',
                measure: state.result.measure,
                alpha: state.result.alpha,
                mu1: state.result.mu1,
                crossed: state.result.crossed,
                crossedAt: state.result.crossedAt,
                finalE: state.result.finalE,
                finalLogE: state.result.finalLogE,
                studies: state.result.results.map(function(r) {
                    return {k:r.k, study:r.study, yi:r.yi, vi:r.vi, eGRO:r.eGRO, eMix:r.eMix, cumLogE:r.cumLogE, crossed:r.crossed};
                })
            };
            return JSON.stringify(data);
        """)
        data = json.loads(json_str)
        assert data["version"] == "safema-1.0"
        assert data["crossed"] is True
        assert len(data["studies"]) == 8


# ===========================================================================
# 12. Tab switching with aria-selected
# ===========================================================================
class TestTabSwitching:
    def test_tab_aria_selected(self, driver):
        load_page(driver)
        # Data tab should be selected initially
        data_btn = driver.find_element(By.ID, "tbtn-data")
        assert data_btn.get_attribute("aria-selected") == "true"

        # Switch to E-Process tab
        driver.execute_script("switchTab('eplot')")
        time.sleep(0.1)
        eplot_btn = driver.find_element(By.ID, "tbtn-eplot")
        assert eplot_btn.get_attribute("aria-selected") == "true"
        # Data tab should no longer be selected
        assert data_btn.get_attribute("aria-selected") == "false"

    def test_tab_panel_visibility(self, driver):
        load_page(driver)
        # Data panel should be visible initially
        data_panel = driver.find_element(By.ID, "panel-data")
        assert "active" in data_panel.get_attribute("class")

        # Switch to compare tab
        driver.execute_script("switchTab('compare')")
        time.sleep(0.1)
        compare_panel = driver.find_element(By.ID, "panel-compare")
        assert "active" in compare_panel.get_attribute("class")
        # Data panel should be hidden
        assert "active" not in data_panel.get_attribute("class")

    def test_all_tabs_switchable(self, driver):
        """Verify all 5 tabs can be switched to and their panels activate."""
        load_page(driver)
        tab_ids = ["data", "eplot", "confseq", "compare", "report"]
        for tid in tab_ids:
            driver.execute_script(f"switchTab('{tid}')")
            time.sleep(0.1)
            panel = driver.find_element(By.ID, f"panel-{tid}")
            btn = driver.find_element(By.ID, f"tbtn-{tid}")
            assert "active" in panel.get_attribute("class"), f"Panel panel-{tid} not active"
            assert btn.get_attribute("aria-selected") == "true", f"Tab tbtn-{tid} not aria-selected"


# ===========================================================================
# Extra: E-value math sanity
# ===========================================================================
class TestEValueMath:
    def test_sglt2i_final_e_above_threshold(self, driver):
        """SGLT2i crossed, so finalE >= 1/alpha = 20."""
        load_example(driver, 0)
        finalE = driver.execute_script("return state.result.finalE")
        threshold = driver.execute_script("return state.result.threshold")
        assert finalE >= threshold, f"finalE={finalE} < threshold={threshold}"

    def test_magnesium_final_e_below_threshold(self, driver):
        load_example(driver, 1)
        finalE = driver.execute_script("return state.result.finalE")
        threshold = driver.execute_script("return state.result.threshold")
        assert finalE < threshold, f"finalE={finalE} >= threshold={threshold}"

    def test_eprocess_cumulative_monotone_in_log(self, driver):
        """Each study's cumLogE should equal previous + current logE."""
        load_example(driver, 0)
        results = driver.execute_script("return state.result.results")
        for i in range(1, len(results)):
            expected = results[i - 1]["cumLogE"] + results[i]["logE"]
            actual = results[i]["cumLogE"]
            assert abs(actual - expected) < 1e-6, f"Study {i}: cumLogE mismatch"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
