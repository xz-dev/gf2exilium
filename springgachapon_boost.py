import os
import asyncio
import argparse
from playwright.async_api import async_playwright

async def boost_with_account(playwright, account, password, boost_links):
    """使用一个账号登录并为所有助力链接助力"""
    browser = await playwright.chromium.launch(headless=True)  # 无头模式
    context = await browser.new_context(
        permissions=['clipboard-read', 'clipboard-write']  # 预先授予剪贴板权限
    )
    page = await context.new_page()
    
    # 登录
    await page.goto("https://gf2exilium.sunborngame.com/springgachapon/main?loginShow=true", wait_until='domcontentloaded')
    await page.fill('input[placeholder="Enter Sunborn Account"]', account)
    await page.fill('input[placeholder="Enter Password"]', password)
    await page.click('div.login_btn img')
    await page.wait_for_load_state()
    print(f"账号 {account} 登录成功")
    
    # 依次访问所有助力链接
    for link in boost_links:
        print(f"访问链接: {link}")
        try:
            # 访问助力链接
            await page.goto(link, wait_until='domcontentloaded')
            
            # 等待跳转到主页
            await page.wait_for_url("https://gf2exilium.sunborngame.com/springgachapon/main", timeout=30*1000)
            print("已成功跳转到主页")
        except Exception as e:
            print(f"访问链接 {link} 失败: {e}")
        
        # 短暂延迟再访问下一个链接
        await asyncio.sleep(2)
    
    # 关闭浏览器
    await browser.close()

def read_links(share_links_file):
    """读取分享链接文件"""
    links = []
    try:
        if os.path.exists(share_links_file):
            with open(share_links_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        links.append(line)
    except Exception as e:
        print(f"读取分享链接文件失败: {e}")
    return links

async def main():
    parser = argparse.ArgumentParser(description="GF2 Exilium Spring Gachapon Boost Helper")
    parser.add_argument("account", help="Sunborn 账号")
    parser.add_argument("password", help="Sunborn 账号密码")
    parser.add_argument("--links", default="share_links.txt", help="分享链接文件路径")
    args = parser.parse_args()
    
    boost_links = read_links(args.links)
    if not boost_links:
        print("没有找到有效的分享链接")
        return
    
    print(f"找到 {len(boost_links)} 个分享链接，准备使用账号 {args.account} 进行助力")
    
    async with async_playwright() as playwright:
        await boost_with_account(playwright, args.account, args.password, boost_links)
        print(f"账号 {args.account} 助力完成")

if __name__ == "__main__":
    asyncio.run(main())