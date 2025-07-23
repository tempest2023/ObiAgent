import sys
from arcadepy import Arcade
from agent.function_nodes.discord_arcade import (
    DiscordGetChannelsNode,
    DiscordSendMessageNode,
)

def discord_oauth_flow():
    client = Arcade()  # Requires ARCADE_API_KEY env variable
    user_id = input("请输入你的用户唯一标识（如邮箱/手机号/用户名）：").strip()
    auth_response = client.auth.start(
        user_id=user_id,
        provider="discord",
        scopes=["identify", "email", "guilds", "guilds.join", "messages.read", "messages.write"],
    )
    if auth_response.status != "completed":
        print("请在浏览器中完成 Discord 授权：")
        print(auth_response.url)
        input("授权完成后请按回车...")
        auth_response = client.auth.wait_for_completion(auth_response)
    if auth_response.status != "completed":
        print("授权失败或未完成")
        sys.exit(1)
    print("授权成功！")
    return user_id

def pocketflow_send_message_workflow(user_id):
    print("\n=== PocketFlow Discord 节点 Demo ===")
    shared = {"user_id": user_id}
    # 1. 获取频道列表
    get_channels_node = DiscordGetChannelsNode()
    action = get_channels_node.run(shared)
    channels = shared.get("discord_channels", [])
    if not channels:
        print("未获取到任何频道，可能没有加入服务器或无权限。")
        sys.exit(1)
    print("你可用的 Discord 频道：")
    for idx, ch in enumerate(channels):
        print(f"{idx+1}. {ch.get('name')} (id: {ch.get('id')}, type: {ch.get('type')})")
    channel_idx = int(input("请选择频道编号：")) - 1
    channel_id = channels[channel_idx].get("id")
    # 2. 发送消息
    msg = input("请输入要发送的消息：")
    send_message_node = DiscordSendMessageNode()
    shared.update({
        "channel_id": channel_id,
        "message": msg
    })
    action = send_message_node.run(shared)
    send_result = shared.get("discord_send_result", {})
    print("消息发送结果：", send_result)

def main():
    print("=== 第一步：Discord 授权 ===")
    user_id = discord_oauth_flow()
    print("\n=== 第二步：PocketFlow Workflow 发送消息 ===")
    pocketflow_send_message_workflow(user_id)

if __name__ == "__main__":
    main() 