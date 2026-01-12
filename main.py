from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
import time
import json

from fastmcp import FastMCP

mcp = FastMCP("Selenium MCP")

class FirefoxAutoBrowser:
    """
    Firefox browser automation encapsulation class,
    implementing core functions of tab management and web page operations
    """
    def __init__(self, command_executor='http://192.168.100.4:4444',
                 firefox_binary_path="C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                 page_load_timeout=30, implicitly_wait=10):
        """
        Initialize browser driver and configuration
        :param command_executor: Remote driver address
        :param firefox_binary_path: Firefox executable file path
        :param page_load_timeout: Page load timeout time
        :param implicitly_wait: Element implicit wait time
        """
        self.driver = None
        self.command_executor = command_executor
        self.firefox_binary_path = firefox_binary_path
        self.page_load_timeout = page_load_timeout
        self.implicitly_wait = implicitly_wait

        self.init_result = self._init_browser()

    def _init_browser(self):
        """
        Private method: Configure Firefox options and initialize Remote driver
        Return: JSON format initialization result
        """
        try:
            firefox_options = FirefoxOptions()
            firefox_options.binary_location = self.firefox_binary_path

            custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
            firefox_options.add_argument(f"--user-agent={custom_user_agent}")

            firefox_options.set_preference("dom.webnotifications.enabled", False)
            firefox_options.set_preference("dom.popup_maximum", -1)
            firefox_options.set_preference("browser.popups.showPopupBlocker", False)
            firefox_options.set_preference("dom.disable_open_during_load", False)
            firefox_options.set_preference("browser.link.open_newwindow", 3)
            firefox_options.set_preference("browser.link.open_newwindow.restriction", 0)

            firefox_options.add_argument("--ignore-certificate-errors")

            self.driver = webdriver.Remote(
                command_executor=self.command_executor,
                options=firefox_options
            )

            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.implicitly_wait(self.implicitly_wait)

            success_json = {
                "code": 200,
                "status": "success",
                "message": "Browser initialized successfully",
                "detail": None,
                "data": None
            }
            return json.dumps(success_json, ensure_ascii=False, indent=2)

        except (WebDriverException, Exception) as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Browser initialization failed: {str(e)}",
                "detail": None,
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

    def create_new_tab(self):
        """
        Function: Create a new blank tab
        Return: JSON format string (contains operation result and related information)
        """
        try:
            if not self.driver:
                raise Exception("Browser driver not initialized")

            self.driver.execute_script("window.open('');")

            result_json = {
                "code": 200,
                "status": "success",
                "message": "New tab created successfully",
                "detail": None,
                "data": None
            }
            return json.dumps(result_json, ensure_ascii=False, indent=2)

        except (WebDriverException, Exception) as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to create new tab: {str(e)}",
                "detail": None,
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

    def get_all_tabs(self):
        """
        Function: Get the list of handles of all current tabs, including detailed tab information
        Return: JSON format string (contains detailed tab information and handle list data)
        """
        try:
            if not self.driver:
                raise Exception("Browser driver not initialized")

            window_handles = self.driver.window_handles
            tab_count = len(window_handles)
            active_handle = None

            try:
                active_handle = self.driver.current_window_handle
            except:
                active_handle = None

            tabs_detail = {
                "total_tabs": tab_count,
                "tabs_info": []
            }
            for index, handle in enumerate(window_handles):
                tab_status = "[Currently Active]" if (active_handle and handle == active_handle) else "[Inactive]"
                tab_info = {
                    "index": index,
                    "handle": handle,
                    "handle_abbr": handle[:20] + "...",
                    "status": tab_status
                }
                tabs_detail["tabs_info"].append(tab_info)

            result_json = {
                "code": 200,
                "status": "success",
                "message": f"Successfully retrieved {tab_count} tabs in total",
                "detail": tabs_detail,
                "data": window_handles
            }
            return json.dumps(result_json, ensure_ascii=False, indent=2)

        except (WebDriverException, Exception) as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to get all tabs: {str(e)}",
                "detail": None,
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

    def get_active_tab(self):
        """
        Function: Get the handle of the currently active (foreground display) tab, including detailed active tab information
        Return: JSON format string (contains active tab details and handle data)
        """
        try:
            if not self.driver:
                raise Exception("Browser driver not initialized")

            current_window = self.driver.current_window_handle
            all_handles = self.driver.window_handles
            tab_count = len(all_handles)
            active_tab_index = all_handles.index(current_window)

            active_detail = {
                "total_tabs": tab_count,
                "active_tab_index": active_tab_index,
                "active_tab_handle": current_window
            }

            result_json = {
                "code": 200,
                "status": "success",
                "message": "Successfully retrieved current active tab information",
                "detail": active_detail,
                "data": current_window
            }
            return json.dumps(result_json, ensure_ascii=False, indent=2)

        except (WebDriverException, Exception) as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to get active tab: {str(e)}",
                "detail": None,
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

    def switch_to_specific_tab(self, target):
        """
        Function: Switch to a specific tab (supports passing handle directly / passing tab index)
        :param target: Target tab (str: tab handle; int: tab index, starting from 0)
        Return: JSON format string (contains switch result and related information)
        """
        try:
            if not self.driver:
                raise Exception("Browser driver not initialized")

            all_handles = self.driver.window_handles
            target_handle = None

            if isinstance(target, int):
                if 0 <= target < len(all_handles):
                    target_handle = all_handles[target]
                else:
                    raise Exception(
                        f"Tab index {target} is invalid, only {len(all_handles)} tabs exist currently (index 0~{len(all_handles) - 1})")
            elif isinstance(target, str):
                if target in all_handles:
                    target_handle = target
                else:
                    raise Exception(f"Tab handle {target} is invalid, not in the current tab list")
            else:
                raise Exception("Invalid parameter type, supports int (index) or str (handle)")

            self.driver.switch_to.window(target_handle)

            result_json = {
                "code": 200,
                "status": "success",
                "message": "Successfully switched to target tab",
                "detail": {
                    "target_param": target,
                    "target_handle": target_handle,
                    "target_handle_abbr": target_handle[:20] + "..."
                },
                "data": None
            }
            return json.dumps(result_json, ensure_ascii=False, indent=2)

        except (WebDriverException, Exception) as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to switch to specific tab: {str(e)}",
                "detail": {
                    "input_target": target
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

    def open_url_in_specific_tab(self, url, target=0):
        """
        Function: Open the specified web page in a specific tab
        :param url: Web page address to open (str)
        :param target: Target tab (str: handle; int: index, default the first tab (index 0))
        Return: JSON format string (contains operation result and related information)
        """
        try:
            if not self.driver:
                raise Exception("Browser driver not initialized")

            if not url or not isinstance(url, str):
                raise Exception("Invalid web page address")

            switch_result = json.loads(self.switch_to_specific_tab(target))
            if switch_result["code"] != 200:
                raise Exception(switch_result["message"])

            self.driver.get(url)

            result_json = {
                "code": 200,
                "status": "success",
                "message": f"Successfully opened web page in target tab: {url}",
                "detail": {
                    "target_tab": target,
                    "opened_url": url
                },
                "data": None
            }
            return json.dumps(result_json, ensure_ascii=False, indent=2)

        except (TimeoutException, WebDriverException) as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Web page loading timed out or failed to open: {str(e)}",
                "detail": {
                    "target_tab": target,
                    "input_url": url
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)
        except (Exception) as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to open web page in specific tab: {str(e)}",
                "detail": {
                    "target_tab": target,
                    "input_url": url
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

    def get_specific_tab_page_content(self, target=None):
        """
        Function: Get the page HTML content of the specified tab (default to get current active tab)
        :param target: Target tab (None: current active tab; str: handle; int: index)
        Return: JSON format string (contains page content length and HTML source data)
        """
        try:
            if not self.driver:
                raise Exception("Browser driver not initialized")

            current_handle = None
            target_info = {}

            if target is None:
                current_handle = self.driver.current_window_handle
                target_info = {
                    "target_type": "current_active",
                    "target_handle": current_handle,
                    "target_handle_abbr": current_handle[:20] + "..."
                }
            else:
                all_handles = self.driver.window_handles
                target_handle = None
                if isinstance(target, int):
                    if 0 <= target < len(all_handles):
                        target_handle = all_handles[target]
                        target_info = {
                            "target_type": "index",
                            "input_target": target,
                            "target_handle": target_handle,
                            "target_handle_abbr": target_handle[:20] + "..."
                        }
                    else:
                        raise Exception(f"Tab index {target} is invalid, only {len(all_handles)} tabs exist currently")
                elif isinstance(target, str):
                    if target in all_handles:
                        target_handle = target
                        target_info = {
                            "target_type": "handle",
                            "input_target": target,
                            "target_handle": target_handle,
                            "target_handle_abbr": target_handle[:20] + "..."
                        }
                    else:
                        raise Exception(f"Tab handle {target} is invalid, not in the current tab list")
                else:
                    raise Exception("Invalid parameter type, supports int (index) or str (handle)")

                self.driver.switch_to.window(target_handle)
                current_handle = target_handle

            page_content = self.driver.page_source
            content_length = len(page_content)

            target_info["content_length"] = content_length

            result_json = {
                "code": 200,
                "status": "success",
                "message": f"Successfully retrieved target tab page content, content length: {content_length} characters",
                "detail": target_info,
                "data": page_content
            }
            return json.dumps(result_json, ensure_ascii=False, indent=2)

        except WebDriverException as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to get tab page content (WebDriver exception): {str(e)}",
                "detail": {
                    "input_target": target
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)
        except Exception as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to get tab page content: {str(e)}",
                "detail": {
                    "input_target": target
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

    def scroll_mouse_wheel_down(self, scroll_distance=500, target_tab=None):
        """
        Function: Simulate mouse wheel scrolling down (supports specifying tab, default current active tab)
        :param scroll_distance: Scrolling distance (pixels, default 500 pixels, larger value means more scrolling)
        :param target_tab: Target tab (None: current active tab; str: handle; int: index)
        Return: JSON format string (contains scrolling operation result)
        """
        try:
            if not self.driver:
                raise Exception("Browser driver not initialized")

            scroll_detail = {
                "scroll_direction": "down",
                "scroll_distance": scroll_distance,
                "target_tab": target_tab
            }

            if target_tab is not None:
                switch_result = json.loads(self.switch_to_specific_tab(target_tab))
                if switch_result["code"] != 200:
                    raise Exception(switch_result["message"])
                scroll_detail["switch_status"] = "Successfully switched to target tab"

            self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")

            result_json = {
                "code": 200,
                "status": "success",
                "message": f"Mouse wheel scrolled down successfully, scrolling distance: {scroll_distance} pixels",
                "detail": scroll_detail,
                "data": None
            }
            return json.dumps(result_json, ensure_ascii=False, indent=2)

        except WebDriverException as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to scroll mouse wheel down (WebDriver exception): {str(e)}",
                "detail": {
                    "scroll_distance": scroll_distance,
                    "target_tab": target_tab
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)
        except Exception as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to scroll mouse wheel down: {str(e)}",
                "detail": {
                    "scroll_distance": scroll_distance,
                    "target_tab": target_tab
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

    def scroll_mouse_wheel_up(self, scroll_distance=500, target_tab=None):
        """
        Function: Simulate mouse wheel scrolling up (supports specifying tab, default current active tab)
        :param scroll_distance: Scrolling distance (pixels, default 500 pixels, larger value means more scrolling)
        :param target_tab: Target tab (None: current active tab; str: handle; int: index)
        Return: JSON format string (contains scrolling operation result)
        """
        try:
            if not self.driver:
                raise Exception("Browser driver not initialized")

            scroll_detail = {
                "scroll_direction": "up",
                "scroll_distance": scroll_distance,
                "target_tab": target_tab
            }

            if target_tab is not None:
                switch_result = json.loads(self.switch_to_specific_tab(target_tab))
                if switch_result["code"] != 200:
                    raise Exception(switch_result["message"])
                scroll_detail["switch_status"] = "Successfully switched to target tab"

            self.driver.execute_script(f"window.scrollBy(0, -{scroll_distance});")

            result_json = {
                "code": 200,
                "status": "success",
                "message": f"Mouse wheel scrolled up successfully, scrolling distance: {scroll_distance} pixels",
                "detail": scroll_detail,
                "data": None
            }
            return json.dumps(result_json, ensure_ascii=False, indent=2)

        except WebDriverException as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to scroll mouse wheel up (WebDriver exception): {str(e)}",
                "detail": {
                    "scroll_distance": scroll_distance,
                    "target_tab": target_tab
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)
        except Exception as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to scroll mouse wheel up: {str(e)}",
                "detail": {
                    "scroll_distance": scroll_distance,
                    "target_tab": target_tab
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

    def click_element_by_xpath(self, xpath, target_tab=None):
        """
        Function: Locate element by XPath expression and execute click operation
        :param xpath: XPath expression for targeting the element (str, required)
        :param target_tab: Target tab (None: current active tab; str: handle; int: index)
        Return: JSON format string (contains element locate and click operation result)
        """
        try:
            if not self.driver:
                raise Exception("Browser driver not initialized")
            if not xpath or not isinstance(xpath, str):
                raise Exception("Invalid XPath expression: it must be a non-empty string")

            click_detail = {
                "xpath_expression": xpath,
                "target_tab": target_tab,
                "operation_status": "not_executed"
            }

            if target_tab is not None:
                switch_result = json.loads(self.switch_to_specific_tab(target_tab))
                if switch_result["code"] != 200:
                    raise Exception(f"Failed to switch to target tab: {switch_result['message']}")
                click_detail["switch_status"] = "Successfully switched to target tab"

            click_detail["operation_status"] = "locating_element"
            target_element = self.driver.find_element(By.XPATH, xpath)
            if not target_element:
                raise NoSuchElementException("Element not found even with valid XPath expression")

            click_detail["operation_status"] = "clicking_element"
            target_element.click()

            click_detail["operation_status"] = "completed_successfully"
            result_json = {
                "code": 200,
                "status": "success",
                "message": "Element located by XPath and clicked successfully",
                "detail": click_detail,
                "data": None
            }
            return json.dumps(result_json, ensure_ascii=False, indent=2)

        except NoSuchElementException as e:
            fail_json = {
                "code": 404,
                "status": "failed",
                "message": f"Element not found by XPath: {str(e)}",
                "detail": {
                    "xpath_expression": xpath,
                    "target_tab": target_tab,
                    "error_type": "NoSuchElementException"
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

        except WebDriverException as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to click element (WebDriver exception): {str(e)}",
                "detail": {
                    "xpath_expression": xpath,
                    "target_tab": target_tab,
                    "error_type": "WebDriverException"
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

        except Exception as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to click element by XPath: {str(e)}",
                "detail": {
                    "xpath_expression": xpath,
                    "target_tab": target_tab,
                    "error_type": "GeneralException"
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

    def click_element(self, locator, locator_type="xpath", target_tab=None):
        """
        Function: Universal element click function, supports multiple locator methods to click any clickable element
        (tags, buttons, links, etc.)
        :param locator: Locator expression (str, required, e.g. id value, XPath expression, CSS selector, etc.)
        :param locator_type: Locator method (str, optional, default "xpath"), support:
            "id", "xpath", "name", "class_name", "css_selector", "tag_name", "link_text", "partial_link_text"
        :param target_tab: Target tab (None: current active tab; str: handle; int: index)
        Return: JSON format string (contains element locate and click operation result)
        """
        supported_locators = {
            "id": By.ID,
            "xpath": By.XPATH,
            "name": By.NAME,
            "class_name": By.CLASS_NAME,
            "css_selector": By.CSS_SELECTOR,
            "tag_name": By.TAG_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT
        }

        try:
            if not self.driver:
                raise Exception("Browser driver not initialized")
            if locator_type not in supported_locators:
                supported_types = ", ".join(supported_locators.keys())
                raise Exception(f"Unsupported locator type: {locator_type}. Supported types: {supported_types}")
            if not locator or not isinstance(locator, str):
                raise Exception("Invalid locator expression: it must be a non-empty string")

            click_detail = {
                "locator_type": locator_type,
                "locator_expression": locator,
                "target_tab": target_tab,
                "operation_status": "not_executed"
            }

            if target_tab is not None:
                switch_result = json.loads(self.switch_to_specific_tab(target_tab))
                if switch_result["code"] != 200:
                    raise Exception(f"Failed to switch to target tab: {switch_result['message']}")
                click_detail["switch_status"] = "Successfully switched to target tab"

            click_detail["operation_status"] = "locating_element"
            by_locator = supported_locators[locator_type]
            target_element = self.driver.find_element(by_locator, locator)

            if not target_element:
                raise NoSuchElementException(f"Element not found even with valid {locator_type} locator")

            click_detail["operation_status"] = "scrolling_to_element"
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_element)
            click_detail["operation_status"] = "clicking_element"
            target_element.click()
            click_detail["operation_status"] = "completed_successfully"
            result_json = {
                "code": 200,
                "status": "success",
                "message": f"Element located by {locator_type} and clicked successfully",
                "detail": click_detail,
                "data": None
            }
            return json.dumps(result_json, ensure_ascii=False, indent=2)

        except NoSuchElementException as e:
            fail_json = {
                "code": 404,
                "status": "failed",
                "message": f"Element not found by {locator_type}: {str(e)}",
                "detail": {
                    "locator_type": locator_type,
                    "locator_expression": locator,
                    "target_tab": target_tab,
                    "error_type": "NoSuchElementException"
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

        except WebDriverException as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to click element (WebDriver exception): {str(e)}",
                "detail": {
                    "locator_type": locator_type,
                    "locator_expression": locator,
                    "target_tab": target_tab,
                    "error_type": "WebDriverException"
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

        except Exception as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to click element by {locator_type}: {str(e)}",
                "detail": {
                    "locator_type": locator_type,
                    "locator_expression": locator,
                    "target_tab": target_tab,
                    "error_type": "GeneralException"
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

    def close_specific_tab(self, target=None):
        """
        Function: Close a specific tab (default to close current active tab, supports specifying handle/index)
        :param target: Target tab (None: current active tab; str: handle; int: index)
        Return: JSON format string (contains close operation result and subsequent switch information)
        """
        try:
            if not self.driver:
                raise Exception("Browser driver not initialized")

            all_handles = self.driver.window_handles
            tab_count_before_close = len(all_handles)
            if tab_count_before_close == 0:
                raise Exception("No available tabs to close currently")

            close_handle = None
            close_detail = {
                "tab_count_before_close": tab_count_before_close,
                "input_target": target
            }
            if target is None:
                close_handle = self.driver.current_window_handle
                close_detail["target_type"] = "current_active"
            else:
                if isinstance(target, int):
                    if 0 <= target < tab_count_before_close:
                        close_handle = all_handles[target]
                        close_detail["target_type"] = "index"
                    else:
                        raise Exception(f"Tab index {target} is invalid, only {tab_count_before_close} tabs exist currently")
                elif isinstance(target, str):
                    if target in all_handles:
                        close_handle = target
                        close_detail["target_type"] = "handle"
                    else:
                        raise Exception(f"Tab handle {target} is invalid, not in the current tab list")
                else:
                    raise Exception("Invalid parameter type, supports int (index) or str (handle)")

            close_detail["closed_handle"] = close_handle
            close_detail["closed_handle_abbr"] = close_handle[:20] + "..."

            self.driver.switch_to.window(close_handle)

            is_last_tab = (tab_count_before_close == 1)
            close_detail["is_last_tab"] = is_last_tab

            self.driver.close()

            if not is_last_tab:
                time.sleep(0.5)
                remaining_handles = self.driver.window_handles
                if len(remaining_handles) > 0:
                    self.driver.switch_to.window(remaining_handles[0])
                    close_detail["post_close_operation"] = "Automatically switched to the first remaining tab"
                    close_detail["switched_to_remaining_handle"] = remaining_handles[0]
            else:
                self.driver = None
                close_detail["post_close_operation"] = "Closed the last tab, browser window exited, driver context invalidated"

            result_json = {
                "code": 200,
                "status": "success",
                "message": f"Successfully closed tab: {close_handle}",
                "detail": close_detail,
                "data": None
            }
            return json.dumps(result_json, ensure_ascii=False, indent=2)

        except WebDriverException as e:
            close_detail = {
                "input_target": target,
                "error_type": "WebDriverException"
            }
            if "Browsing context has been discarded" in str(e) or "NoSuchWindowError" in str(e):
                self.driver = None
                close_detail["error_detail"] = "Browsing context invalidated (tab/browser closed), cannot continue operation"
                message = "Browsing context invalidated (tab/browser closed), cannot continue operation"
            else:
                close_detail["error_detail"] = str(e)
                message = f"Failed to close specific tab: {str(e)}"

            fail_json = {
                "code": 500,
                "status": "failed",
                "message": message,
                "detail": close_detail,
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)
        except Exception as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to close specific tab: {str(e)}",
                "detail": {
                    "input_target": target
                },
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

    def quit_browser(self):
        """
        Function: Close all tabs and exit browser driver, release resources
        Return: JSON format string (contains exit operation result)
        """
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None

            result_json = {
                "code": 200,
                "status": "success",
                "message": "Browser exited successfully, resources released",
                "detail": None,
                "data": None
            }
            return json.dumps(result_json, ensure_ascii=False, indent=2)

        except (WebDriverException, Exception) as e:
            fail_json = {
                "code": 500,
                "status": "failed",
                "message": f"Failed to quit browser: {str(e)}",
                "detail": None,
                "data": None
            }
            return json.dumps(fail_json, ensure_ascii=False, indent=2)

browser = None
try:
    browser = FirefoxAutoBrowser()
except Exception as init_error:
    browser = None

@mcp.tool()
def create_new_tab() -> str:
    """
    功能：创建一个新的空白浏览器标签页
    返回：JSON格式字符串，包含创建操作的成功/失败状态及相关提示信息
    """
    if browser is None:
        fail_json = {
            "code": 500,
            "status": "failed",
            "message": "浏览器实例未初始化，无法创建新标签页",
            "detail": None,
            "data": None
        }
        return json.dumps(fail_json, ensure_ascii=False, indent=2)
    return browser.create_new_tab()

@mcp.tool()
def get_all_tabs() -> str:
    """
    功能：获取当前浏览器中所有标签页的详细信息
    返回：JSON格式字符串，包含标签页总数、每个标签的索引、句柄、激活状态等详细数据
    """
    if browser is None:
        fail_json = {
            "code": 500,
            "status": "failed",
            "message": "浏览器实例未初始化，无法获取标签页列表",
            "detail": None,
            "data": None
        }
        return json.dumps(fail_json, ensure_ascii=False, indent=2)
    return browser.get_all_tabs()

@mcp.tool()
def get_active_tab() -> str:
    """
    功能：获取当前处于激活状态（前台显示）的标签页详细信息
    返回：JSON格式字符串，包含激活标签的索引、句柄及当前总标签数等信息
    """
    if browser is None:
        fail_json = {
            "code": 500,
            "status": "failed",
            "message": "浏览器实例未初始化，无法获取激活标签页",
            "detail": None,
            "data": None
        }
        return json.dumps(fail_json, ensure_ascii=False, indent=2)
    return browser.get_active_tab()

@mcp.tool()
def switch_to_specific_tab(target) -> str:
    """
    功能：切换到指定的浏览器标签页
    参数：target - 目标标签页标识（整数：标签索引，从0开始；字符串：标签句柄）
    返回：JSON格式字符串，包含切换操作的成功/失败状态及目标标签的相关信息
    """
    if browser is None:
        fail_json = {
            "code": 500,
            "status": "failed",
            "message": "浏览器实例未初始化，无法切换标签页",
            "detail": {"input_target": target},
            "data": None
        }
        return json.dumps(fail_json, ensure_ascii=False, indent=2)
    return browser.switch_to_specific_tab(target)

@mcp.tool()
def open_url_in_specific_tab(url: str, target=0) -> str:
    """
    功能：在指定的浏览器标签页中打开指定的网页地址
    参数：
        url - 要打开的网页地址（字符串，必填）
        target - 目标标签页标识（整数：标签索引；字符串：标签句柄，默认值0，即第一个标签页）
    返回：JSON格式字符串，包含网页打开操作的成功/失败状态及相关详情
    """
    if browser is None:
        fail_json = {
            "code": 500,
            "status": "failed",
            "message": "浏览器实例未初始化，无法打开网页",
            "detail": {"target_tab": target, "input_url": url},
            "data": None
        }
        return json.dumps(fail_json, ensure_ascii=False, indent=2)
    return browser.open_url_in_specific_tab(url, target)

@mcp.tool()
def get_specific_tab_page_content(target=None) -> str:
    """
    功能：获取指定标签页的网页HTML完整内容
    参数：target - 目标标签页标识（None：当前激活标签；整数：标签索引；字符串：标签句柄，默认None）
    返回：JSON格式字符串，包含网页内容长度及完整HTML源码数据
    """
    if browser is None:
        fail_json = {
            "code": 500,
            "status": "failed",
            "message": "浏览器实例未初始化，无法获取网页内容",
            "detail": {"input_target": target},
            "data": None
        }
        return json.dumps(fail_json, ensure_ascii=False, indent=2)
    return browser.get_specific_tab_page_content(target)

@mcp.tool()
def scroll_mouse_wheel_down(scroll_distance=500, target_tab=None) -> str:
    """
    功能：模拟鼠标滚轮向下滚动指定距离
    参数：
        scroll_distance - 滚动距离（像素，默认500像素，值越大滚动幅度越大）
        target_tab - 目标标签页标识（None：当前激活标签；整数：标签索引；字符串：标签句柄，默认None）
    返回：JSON格式字符串，包含滚动操作的成功/失败状态及相关详情
    """
    if browser is None:
        fail_json = {
            "code": 500,
            "status": "failed",
            "message": "浏览器实例未初始化，无法执行滚动操作",
            "detail": {"scroll_distance": scroll_distance, "target_tab": target_tab},
            "data": None
        }
        return json.dumps(fail_json, ensure_ascii=False, indent=2)
    return browser.scroll_mouse_wheel_down(scroll_distance, target_tab)

@mcp.tool()
def scroll_mouse_wheel_up(scroll_distance=500, target_tab=None) -> str:
    """
    功能：模拟鼠标滚轮向上滚动指定距离
    参数：
        scroll_distance - 滚动距离（像素，默认500像素，值越大滚动幅度越大）
        target_tab - 目标标签页标识（None：当前激活标签；整数：标签索引；字符串：标签句柄，默认None）
    返回：JSON格式字符串，包含滚动操作的成功/失败状态及相关详情
    """
    if browser is None:
        fail_json = {
            "code": 500,
            "status": "failed",
            "message": "浏览器实例未初始化，无法执行滚动操作",
            "detail": {"scroll_distance": scroll_distance, "target_tab": target_tab},
            "data": None
        }
        return json.dumps(fail_json, ensure_ascii=False, indent=2)
    return browser.scroll_mouse_wheel_up(scroll_distance, target_tab)

@mcp.tool()
def click_element_by_xpath(xpath: str, target_tab=None) -> str:
    """
    功能：通过XPath表达式定位指定标签页中的元素，并执行点击操作
    参数：
        xpath - XPath定位表达式（字符串，必填，用于精准定位页面元素）
        target_tab - 目标标签页标识（None：当前激活标签；整数：标签索引；字符串：标签句柄，默认None）
    返回：JSON格式字符串，包含元素定位及点击操作的成功/失败状态及相关详情
    """
    if browser is None:
        fail_json = {
            "code": 500,
            "status": "failed",
            "message": "浏览器实例未初始化，无法执行元素点击操作",
            "detail": {"xpath_expression": xpath, "target_tab": target_tab},
            "data": None
        }
        return json.dumps(fail_json, ensure_ascii=False, indent=2)
    return browser.click_element_by_xpath(xpath, target_tab)

@mcp.tool()
def click_element(locator: str, locator_type="xpath", target_tab=None) -> str:
    """
    功能：通用元素点击函数，支持多种定位方式定位并点击页面元素（按钮、链接等）
    参数：
        locator - 元素定位表达式（字符串，必填，如id值、CSS选择器、XPath表达式等）
        locator_type - 定位方式（字符串，可选，默认"xpath"，支持id、name、css_selector等8种方式）
        target_tab - 目标标签页标识（None：当前激活标签；整数：标签索引；字符串：标签句柄，默认None）
    返回：JSON格式字符串，包含元素定位及点击操作的成功/失败状态及相关详情
    """
    if browser is None:
        fail_json = {
            "code": 500,
            "status": "failed",
            "message": "浏览器实例未初始化，无法执行元素点击操作",
            "detail": {"locator_expression": locator, "locator_type": locator_type, "target_tab": target_tab},
            "data": None
        }
        return json.dumps(fail_json, ensure_ascii=False, indent=2)
    return browser.click_element(locator, locator_type, target_tab)

@mcp.tool()
def close_specific_tab(target=None) -> str:
    """
    功能：关闭指定的浏览器标签页
    参数：target - 目标标签页标识（None：当前激活标签；整数：标签索引；字符串：标签句柄，默认None）
    返回：JSON格式字符串，包含关闭操作的成功/失败状态及关闭后的标签页切换信息
    """
    if browser is None:
        fail_json = {
            "code": 500,
            "status": "failed",
            "message": "浏览器实例未初始化，无法关闭标签页",
            "detail": {"input_target": target},
            "data": None
        }
        return json.dumps(fail_json, ensure_ascii=False, indent=2)
    return browser.close_specific_tab(target)

@mcp.tool()
def quit_browser() -> str:
    """
    功能：关闭所有浏览器标签页，退出浏览器驱动并释放相关系统资源
    返回：JSON格式字符串，包含浏览器退出操作的成功/失败状态及相关提示信息
    """
    if browser is None:
        fail_json = {
            "code": 500,
            "status": "failed",
            "message": "浏览器实例未初始化，无需执行退出操作",
            "detail": None,
            "data": None
        }
        return json.dumps(fail_json, ensure_ascii=False, indent=2)
    return browser.quit_browser()

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001, path="/mcp")
