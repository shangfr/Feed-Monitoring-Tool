# Feed-Monitoring-Tool
>  Streamlit应用：Feed资讯实时监控(Feed-Monitoring-Tool)



基于`协程`和`定时器`实现`异步`定时协程解析Feed信息源，将包含`关键词`的资讯进行保存，并通过飞书`机器人`推送至聊天群组。

Libraries used:
- `streamlit` - [Web Framework](https://docs.streamlit.io/library/cheatsheet)
- `feedparser` - [Parse Atom and RSS feeds in Python](https://feedparser.readthedocs.io/en/latest/introduction.html)
- `asyncio` - [Allows concurrent input/output processing](https://docs.python.org/3/library/asyncio.html)
- `pandas` -  [Python Data Analysis Library](https://pandas.pydata.org/)

### 使用说明

1. 配置*Feed*消息源（*RSS*、Atom），监控关键词（空格分割）和监控内容（标题、摘要），设置监控间隔时间；
2. 🚗运行、⛔️暂停、🆑清空、🔁更新；
3. 在状态栏可查看当前监控设置情况；

<img src="C:\Users\86155\Desktop\Feed-Monitoring-Tool\static\fig1.png" style="zoom:50%;" />

4. 点击🚗启动运行程序，状态栏显示当前匹配信息，同时显示最新匹配到的新闻标题；

<img src="C:\Users\86155\Desktop\Feed-Monitoring-Tool\static\fig2.png" style="zoom:50%;" />

5. 点击详情页面，可以查看最近的匹配数据。（点击🔁进行数据更新）

<img src="C:\Users\86155\Desktop\Feed-Monitoring-Tool\static\fig3.png" style="zoom:50%;" />

6. 数据详情处，双击链接可进行页面跳转。

### 监控信息发送
通过**webhook**发送监控信息至：
- **飞书**：[在飞书捷径中使用 Webhook 触发器](https://www.feishu.cn/hc/zh-CN/articles/360040566333-%E5%9C%A8%E9%A3%9E%E4%B9%A6%E6%8D%B7%E5%BE%84%E4%B8%AD%E4%BD%BF%E7%94%A8-webhook-%E8%A7%A6%E5%8F%91%E5%99%A8)
-  **钉钉**：[使用Webhook发送群聊消息](https://open.dingtalk.com/document/orgapp/assign-a-webhook-url-to-an-internal-chatbot)
-  **微信**：[群机器人Webhook地址设置](https://open.work.weixin.qq.com/help2/pc/14931?is_tencent=0&version=4.0.12.6015&platform=win)




### [Feed消息源](https://post.smzdm.com/p/axlx4g43/?sort_tab=hot%252F)

- *有 RSS 的网站*
如果网站提供了 RSS 服务。那么在网站的顶部、右侧、底部等地方，通常就会有一个橙色的 WiFi的图标，它就是 RSS ，点击即可获取链接。
- <img src="C:\Users\86155\Desktop\Feed-Monitoring-Tool\static\pic01.jpg" style="zoom: 80%;" />


- *没 RSS 的网站*

- 可以使用[**RSSHub**](https://docs.rsshub.app/zh/)生成订阅源，感谢 [RSSHub](https://docs.rsshub.app/) 项目，它可以给各种奇奇怪怪的网站生成了 RSS 订阅源，堪称**万物皆可 RSS**。RSSHub适配了300多个网站，上千个内容。涵盖了知乎、微博、豆瓣、B站、贴吧、斗鱼、虎牙、网易云音乐等国内外主流网站。

<img src="C:\Users\86155\Desktop\Feed-Monitoring-Tool\static\pic02.jpg" style="zoom:80%;" />

添加订阅时，只需要将举例中的 UID 换成你想要订阅博主的 UID 即可。

<img src="C:\Users\86155\Desktop\Feed-Monitoring-Tool\static\pic03.jpg" style="zoom: 80%;" />

此外，如果你要订阅的内容多为国外网站，那么还可以尝试一下 [RSS Bridge](https://sebsauvage.net/rss-bridge/) 这个项目。

<img src="C:\Users\86155\Desktop\Feed-Monitoring-Tool\static\pic04.jpg" style="zoom:80%;" />
