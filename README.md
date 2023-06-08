# 部署在vercel上的Vocechat的api
:bangbang: vercel部署可能出现问题，openai响应超过10秒以上会直接time out。
直接在vercel上部署，部署方便~

## 使用方法
1. fork
2. 进入vercel，add new project
3. import中选中fork好的项目
4. Environment Variables对应填入如下参数

| Name|Value|
|-|-|
| VOCE_BOT_ID |放入在vocechat中可以找到机器人的id|
|VOCE_SECRET|放入在vocechat中可以找到机器人的SECRET|
|VOCE_URL|填入vocechat的地址，如https://voce.chat|
|MONGO_URI|填入数据库地址|
|OPENAI_KEY|填入openai的key|

## 数据库的作用
采用的mongo远程数据库，在开启上下文聊天模式以后，数据库用来记录与ai的聊天记录；
