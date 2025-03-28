import asyncio
import argparse
from playwright.async_api import async_playwright


async def run(playwright, account, password):
    # 创建浏览器上下文并预先授予权限
    browser = await playwright.chromium.launch(headless=True)  # 无头模式
    context = await browser.new_context(
        permissions=["clipboard-read", "clipboard-write"]  # 预先授予剪贴板权限
    )
    page = await context.new_page()

    # 进入指定网页，不等待页面完全加载
    retry = 3
    while retry > 0:
        try:
            await page.goto(
                "https://gf2exilium.sunborngame.com/springgachapon/main?loginShow=true",
                wait_until="domcontentloaded",
            )
            # 输入账号
            await page.fill('input[placeholder="Enter Sunborn Account"]', account)
            # 输入密码
            await page.fill('input[placeholder="Enter Password"]', password)
            # 点击登录按钮
            await page.click("div.login_btn img")
            # 等待页面跳转到游戏主界面
            await page.wait_for_load_state(timeout=60 * 1000)
            await page.goto(
                "https://gf2exilium.sunborngame.com/springgachapon/?isShare=true",
                wait_until="domcontentloaded",
            )

            break
        except Exception as e:
            print(f"登录时出错: {e}")
            retry -= 1

    # 进入任务菜单
    await page.click('div.game-main-bottom div.game-log img[src*="game-get.png"]')

    # 等待任务列表加载
    await page.wait_for_selector("div.task-content-div")

    # 获取任务列表
    tasks = await page.query_selector_all("div.task-item-div")

    for task in tasks:
        # 输出任务文本
        task_name = await task.query_selector("div.task-text-div")
        task_text = await task_name.inner_text()
        print(f"任务: {task_text.strip()}")

        if "Friend Boost" in task_text and "10 / 10" in task_text:
            print("好友助力任务已完成")
            continue
        # 点击任务右边的按钮去完成任务
        task_button = await task.query_selector("div.task-go-btn")
        await task_button.click()
        await asyncio.sleep(3)
        await page.mouse.click(500, 500)
        await task_button.click()
        await asyncio.sleep(2)
        await page.mouse.click(500, 500)
        print("任务已点击")

    # 刷新页面
    await page.reload()

    # 抽卡逻辑
    while True:
        await asyncio.sleep(3)
        # 获取剩余次数
        remaining_attempts = await page.query_selector("div.remainder-game-div div.num")
        if remaining_attempts:
            attempts_text = await remaining_attempts.inner_text()
            print(f"剩余抽卡次数: {attempts_text}")

            if attempts_text == "0":
                print("抽卡次数已用完")
                break

            # 点击抽卡按钮
            egg_btn = await page.query_selector("div.game-egg-btn")
            if egg_btn:
                await egg_btn.click()
                print("点击抽卡按钮")

                # 等待动画完成
                await asyncio.sleep(5)

                # 点击任意位置关闭抽卡结果
                await page.reload()
            else:
                print("未找到抽卡按钮")
                break
        else:
            print("未找到剩余次数显示")
            break

    print("抽卡完成")
    print("任务成功全部完成")
    # 关闭浏览器
    # input("Press Enter to close the browser...")
    await browser.close()


async def main(account, password):
    async with async_playwright() as playwright:
        await run(playwright, account, password)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Login to GF2 Exilium Spring Gachapon")
    parser.add_argument("account", help="Sunborn account")
    parser.add_argument("password", help="Sunborn password")
    args = parser.parse_args()

    asyncio.run(main(args.account, args.password))
