"""
简道云自动化工具 - Playwright版本
使用 Playwright 实现更快速、更可靠的自动化
内置用户名和密码
"""

from playwright.sync_api import sync_playwright
import time
import json
import logging

# 内置登录凭证
USERNAME = "15694429449"
PASSWORD = "Aa-15694429449"

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JDYAutomationPlaywright:
    """简道云自动化 Playwright 类"""
    
    def __init__(self, headless=False):
        """
        初始化自动化工具
        
        Args:
            headless: 是否使用无头模式
        """
        self.username = USERNAME
        self.password = PASSWORD
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    def setup_browser(self):
        """设置 Playwright 浏览器"""
        logger.info("正在设置浏览器...")
        
        self.playwright = sync_playwright().start()
        
        # 启动 Chromium 浏览器
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        # 创建浏览器上下文
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 创建新页面
        self.page = self.context.new_page()
        
        # 设置默认超时
        self.page.set_default_timeout(20000)
        
        logger.info("浏览器设置完成")
        
    def login(self, manual_verify=True):
        """
        登录到简道云
        
        Args:
            manual_verify: 是否允许手动处理验证
            
        Returns:
            bool: 登录是否成功
        """
        try:
            logger.info("打开登录页面...")
            self.page.goto("https://www.jdy.com/login/", wait_until="networkidle")
            self.page.wait_for_load_state("domcontentloaded")
            
            logger.info(f"输入用户名: {self.username}")
            
            # 尝试多种可能的用户名输入框选择器
            username_selectors = [
                "#username",
                "input[name='username']",
                "input[type='text']",
                "input[placeholder*='用户名']",
                "input[placeholder*='账号']"
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        username_input = self.page.locator(selector).first
                        if username_input.is_visible():
                            break
                except:
                    continue
            
            if not username_input:
                logger.error("未找到用户名输入框")
                self.page.screenshot(path="error_no_username_input.png")
                return False
            
            username_input.fill(self.username)
            
            # 尝试多种可能的密码输入框选择器
            password_selectors = [
                "#password",
                "input[name='password']",
                "input[type='password']",
                "input[placeholder*='密码']"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        password_input = self.page.locator(selector).first
                        if password_input.is_visible():
                            break
                except:
                    continue
            
            if not password_input:
                logger.error("未找到密码输入框")
                self.page.screenshot(path="error_no_password_input.png")
                return False
            
            password_input.fill(self.password)
            
            # 勾选用户协议和隐私政策复选框
            logger.info("勾选用户协议和隐私政策...")
            agreement_selectors = [
                "#reg_agreement",  # 精确匹配ID
                "input#reg_agreement",
                "input[type='checkbox'][id='reg_agreement']",
                "input[type='checkbox']"
            ]
            
            agreement_checkbox = None
            for selector in agreement_selectors:
                try:
                    locator = self.page.locator(selector)
                    if locator.count() > 0:
                        # 获取第一个可见的checkbox
                        elem = locator.first
                        if elem.is_visible():
                            agreement_checkbox = elem
                            logger.info(f"找到协议复选框: {selector}")
                            break
                except:
                    continue
            
            if agreement_checkbox:
                # 检查是否已经勾选
                try:
                    is_checked = agreement_checkbox.is_checked()
                    if not is_checked:
                        agreement_checkbox.check()
                        logger.info("已勾选用户协议复选框")
                        self.page.wait_for_timeout(500)
                    else:
                        logger.info("用户协议复选框已经勾选")
                except:
                    logger.warning("无法勾选用户协议，继续执行...")
            else:
                logger.warning("未找到用户协议复选框，可能不需要勾选")
            
            # 查找登录按钮
            login_button_selectors = [
                "#login_btn",  # 精确匹配登录按钮ID
                "input#login_btn",
                "input[type='button'][id='login_btn']",
                "input[value='登录']",
                ".login-button",
                "button[type='submit']",
                "text=登录",
                "button:has-text('登录')"
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        login_button = self.page.locator(selector).first
                        if login_button.is_visible():
                            break
                except:
                    continue
            
            if not login_button:
                logger.error("未找到登录按钮")
                self.page.screenshot(path="error_no_login_button.png")
                return False
            
            logger.info("点击登录按钮...")
            login_button.click()
            
            # 等待页面响应
            self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # 检查是否有弹窗需要点击同意
            logger.info("检查是否有同意弹窗...")
            popup_agree_selectors = [
                "#agree-protocol",  # 精确匹配弹窗同意按钮ID
                "a#agree-protocol",
                "a[id='agree-protocol']",
                "a.lr_btn2",
                "text=同意",
                "button:has-text('同意')",
                "a:has-text('同意')",
                "text=确定",
                "button:has-text('确定')",
                "text=我知道了",
                "button:has-text('我知道了')",
                "[class*='confirm']",
                "[class*='agree']"
            ]
            
            popup_found = False
            for selector in popup_agree_selectors:
                try:
                    locator = self.page.locator(selector)
                    if locator.count() > 0:
                        for i in range(locator.count()):
                            elem = locator.nth(i)
                            if elem.is_visible():
                                logger.info(f"发现弹窗按钮: {selector}")
                                elem.click()
                                logger.info("已点击同意按钮")
                                popup_found = True
                                self.page.wait_for_timeout(2000)
                                break
                    if popup_found:
                        break
                except Exception as e:
                    continue
            
            if not popup_found:
                logger.info("未发现弹窗，直接进入首页")
            
            # 等待页面加载
            logger.info("等待页面加载...")
            self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # 查找并点击"进入使用"按钮
            logger.info("查找'进入使用'按钮...")
            enter_button_selectors = [
                "button.serviceStartStatus__Zssvi",
                "button.kd-btn.serviceStartStatus__Zssvi",
                "button:has-text('进入使用')",
                "text=进入使用",
                "button.kd-btn-second:has-text('进入使用')",
                "button span:has-text('进入使用')"
            ]
            
            enter_button_found = False
            for selector in enter_button_selectors:
                try:
                    locator = self.page.locator(selector)
                    if locator.count() > 0:
                        elem = locator.first
                        if elem.is_visible():
                            logger.info(f"找到'进入使用'按钮: {selector}")
                            elem.click()
                            logger.info("已点击'进入使用'按钮")
                            enter_button_found = True
                            self.page.wait_for_load_state("networkidle", timeout=10000)
                            break
                except Exception as e:
                    continue
            
            if not enter_button_found:
                logger.warning("未找到'进入使用'按钮，可能已经在业务系统首页")
            
            # 等待登录完成
            logger.info("等待登录完成...")
            self.page.wait_for_load_state("networkidle", timeout=10000)
            
            # 检查是否需要手动验证
            current_url = self.page.url
            if "login" in current_url.lower() and manual_verify:
                logger.warning("可能需要手动处理验证码或其他验证...")
                input("请在浏览器中完成验证，然后按回车继续...")
                self.page.wait_for_load_state("networkidle", timeout=10000)
                current_url = self.page.url
            
            # 验证是否登录成功
            if "index.html" in current_url or "home" in current_url:
                logger.info("登录成功！")
                return True
            else:
                logger.warning(f"当前URL: {current_url}")
                logger.warning("登录状态不确定")
                return False
                
        except Exception as e:
            logger.error(f"登录过程出错: {str(e)}")
            self.page.screenshot(path="error_login.png")
            return False
    
    def navigate_to_homepage(self):
        """导航到首页"""
        try:
            logger.info("导航到首页...")
            self.page.goto("https://tf.jdy.com/ierp/index.html?formId=home_page", wait_until="networkidle")
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            logger.info("已到达首页")
            return True
        except Exception as e:
            logger.error(f"导航到首页出错: {str(e)}")
            self.page.screenshot(path="error_navigate_homepage.png")
            return False
    
    def wait_for_page_load(self):
        """等待页面加载完成"""
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
    
    def navigate_to_sales_order(self):
        """导航到销售订单页面"""
        try:
            logger.info("查找销售管理菜单...")
            
            # 等待页面加载
            self.wait_for_page_load()
            
            # 尝试多种选择器查找销售管理
            sales_management_selectors = [
                "text=销售管理",
                "span:has-text('销售管理')",
                "div:has-text('销售管理')",
                "li:has-text('销售管理')",
                "a:has-text('销售管理')",
                "[class*='menu'] >> text=销售管理"
            ]
            
            sales_management = None
            for selector in sales_management_selectors:
                try:
                    locator = self.page.locator(selector)
                    if locator.count() > 0:
                        for i in range(locator.count()):
                            elem = locator.nth(i)
                            if elem.is_visible():
                                sales_management = elem
                                logger.info(f"找到销售管理菜单: {selector}")
                                break
                    if sales_management:
                        break
                except:
                    continue
            
            if not sales_management:
                logger.error("未找到销售管理菜单")
                self.page.screenshot(path="debug_no_sales_menu.png")
                logger.info("已保存截图: debug_no_sales_menu.png")
                return False
            
            # 滚动到元素可见
            sales_management.scroll_into_view_if_needed()
            self.page.wait_for_timeout(1000)
            
            # 鼠标悬停
            logger.info("鼠标悬停在销售管理菜单...")
            sales_management.hover()
            self.page.wait_for_timeout(2000)
            
            # 查找销售出库子菜单
            logger.info("查找销售订单子菜单...")
            sales_outbound_selectors = [
                "text=销售订单",
                "span:has-text('销售订单')",
                "div:has-text('销售订单')",
                "li:has-text('销售订单')",
                "a:has-text('销售订单')"
            ]
            
            sales_outbound = None
            for selector in sales_outbound_selectors:
                try:
                    locator = self.page.locator(selector)
                    if locator.count() > 0:
                        for i in range(locator.count()):
                            elem = locator.nth(i)
                            if elem.is_visible():
                                sales_outbound = elem
                                logger.info(f"找到销售订单菜单: {selector}")
                                break
                    if sales_outbound:
                        break
                except:
                    continue
            
            if not sales_outbound:
                logger.error("未找到销售订单子菜单")
                self.page.screenshot(path="debug_no_sales_outbound.png")
                logger.info("已保存截图: debug_no_sales_outbound.png")
                return False
            
            # 点击销售出库
            logger.info("点击销售订单...")
            sales_outbound.click()
            
            self.page.wait_for_load_state("networkidle", timeout=10000)
            self.wait_for_page_load()
            
            logger.info("已进入销售订单页面")
            return True
            
        except Exception as e:
            logger.error(f"导航到销售订单出错: {str(e)}")
            self.page.screenshot(path="error_navigate_sales.png")
            return False
    
    def close(self):
        """关闭浏览器"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭浏览器出错: {str(e)}")
    
    def run(self):
        """执行完整的自动化流程"""
        try:
            # 设置浏览器
            self.setup_browser()
            
            # 登录
            if not self.login():
                logger.warning("登录可能失败，但继续执行...")
            
            # 导航到首页
            if not self.navigate_to_homepage():
                return []
            
            # 导航到销售订单
            if not self.navigate_to_sales_order():
                return []
            
            # 点击历史单据
            # if not self.click_history_orders():
            #     return []
            
            # # 获取列表数据
            # data = self.get_list_data()
            
            # # 保存数据
            # if data:
            #     self.save_data(data)
            
            return []
            
        except Exception as e:
            logger.error(f"执行过程出错: {str(e)}")
            return []
        finally:
            # 保持浏览器打开以便查看结果
            logger.info("=" * 50)
            input("按回车键关闭浏览器...")
            self.close()


def main():
    """主函数"""
    print("=" * 50)
    print("简道云自动化工具 - Playwright版本")
    print("=" * 50)
    print(f"用户名: {USERNAME}")
    print(f"密码: {'*' * len(PASSWORD)}")
    print("=" * 50)
    
    # 是否使用无头模式
    headless_input = input("是否使用无头模式? (y/n, 默认n): ").strip().lower()
    headless = headless_input == 'y'
    
    # 创建自动化实例
    automation = JDYAutomationPlaywright(headless)
    
    # 运行自动化流程
    data = automation.run()
    
    # 输出结果
    print("\n" + "=" * 50)
    print("执行完成！")
    print("=" * 50)
    if data:
        print(f"获取到 {len(data)} 条数据")
        print("\n数据预览:")
        for i, item in enumerate(data[:5]):  # 只显示前5条
            print(f"{i+1}. {item}")
    else:
        print("未获取到数据")


if __name__ == "__main__":
    main()
