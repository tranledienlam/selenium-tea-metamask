import argparse
import random
from selenium.webdriver.common.by import By

from browser_automation import BrowserManager, Node
from utils import Utility
from metamask import Auto as MetaMaskAuto, Setup as MetaMaskSetup, EXTENSION_URL as METAMASK_EXTENSION_URL

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.metaMask = MetaMaskAuto(node, profile)
        self.profile_name = profile.get('profile_name')
        self.password = profile.get('password')
        self.receive_address = [
            '0x73e91fa6fac157e9f814b00d8abf20dfdccc28f6',
            '0x0765ddaade239da020a510324cfd0cec05772488',
            '0xa028341248122862b459926bdf74f93a65d21f27',
        ]
    def send_token(self):
        random_address = random.choice(self.receive_address)
        random_amount = f"{random.uniform(0.1, 0.3):.6f}"

        actions_send_token = [
            (self.node.find_and_click, By.CSS_SELECTOR, '[data-testid="eth-overview-send"]'),
            (self.node.find_and_input, By.CSS_SELECTOR, '[data-testid="ens-input"]', random_address, None, 0),
            (self.node.find_and_input, By.CSS_SELECTOR, '[data-testid="currency-input"]', random_amount, None, 0.1),
            (self.node.find_and_click, By.XPATH, '//button[text()="Continue"]'),
            (self.node.find_and_click, By.XPATH, '//button[text()="Confirm"]'),
        ]

        if not self.node.execute_chain(actions=actions_send_token, message_error='Send eth thất bại'):
            return False
        
        if self.node.find(By.CLASS_NAME, 'transaction-status-label', None, 10):
            times = 10
            while times > 0:
                status_tx = self.node.get_text(
                    By.CLASS_NAME, 'transaction-status-label')
                if status_tx in ['Confirmed', 'Failed']:
                    return True
                if status_tx == 'Pending':
                    pass

                times = times - 1
                Utility.wait_time(2)
        
        return True
        
    def _run(self):
        self.metaMask._run()
        self.metaMask.change_network(network_name='Tea Sepolia Testnet', 
                            rpc_url='https://tea-sepolia.g.alchemy.com/public',
                            chain_id='10218', 
                            symbol='TEA', 
                            block_explorer='https://sepolia.tea.xyz')
        times = 10
        for i in range(times):
            if not self.send_token():
                self.node.log(f'Send token thành công {i}/{times}')
                break
            Utility.wait_time(10)
        
        self.node.snapshot(message=f'Send token thành công {times} lần')
        return True
    
class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        self.metaMask = MetaMaskSetup(node, profile)
        
    def _run(self):
        self.metaMask._run()
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    profiles = Utility.get_data('profile_name', 'password', 'seeds')
        
    if not profiles:
        print("Không có dữ liệu để chạy")
        exit()

    browser_manager = BrowserManager(AutoHandlerClass=Auto, SetupHandlerClass=Setup)
    browser_manager.config_extension('meta-wallet-*.crx')
    # browser_manager.run_browser(profiles[1])
    browser_manager.run_terminal(
        profiles=profiles,
        max_concurrent_profiles=4,
        block_media=True,
        auto=args.auto,
        headless=args.headless,
        disable_gpu=args.disable_gpu,
    )