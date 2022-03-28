# demo

## 视频演示1 - 1-1关卡，任意英雄
https://www.bilibili.com/video/BV1Kq4y1g77h/
对应1-1.py

## 视频演示2 - 2-5关卡，晨拥，米尔豪斯，暴龙王
https://www.bilibili.com/video/BV1Er4y1C7nV/
对应2-5.py

## 使用说明演示视频: 
[video placeholder]

## 使用方法：
### 环境配置
- 进入cmd
   - cmd就是command line，进入方式: 在`win+r` 里打 `cmd` 即可进入
   - 或者在 `开始` 键后输入 `cmd`, 并进入
- 建立log.config
   - 这里需要在 `%localappdata%\Local\Blizzard\Hearthstone\` 文件夹下建立一个文件，文件名是 `log.config`, 文件内容是
    ```
    [Power]
    LogLevel=1
    FilePrinting=True
    ConsolePrinting=False
    ScreenPrinting=False
    Verbose=True
    ```
- 确认power.log正常输出
    - log.config 建立好之后，启动游戏，此时会在 `%programfiles(x86)%\Hearthstone\Logs\`下产生 `power.log`文件，且游戏终止时会自动删除 
    - 确认power.log内容正常输出即可
- 安装python3
    - 参看网络内容或[链接](https://docs.qq.com/doc/DZGpPVXZHQktkbnBX)
    - 确认成功安装: 在cmd中打 `python -V` 显示版本号即可
- 安装pip
    - 参看网络内容或[链接](https://docs.qq.com/doc/DZGpPVXZHQktkbnBX)
    - 确认成功安装：在cmd中打 `pip`，有解释内容即可
- 安装所需依赖包
    - 下载requirements.txt, 进入cmd， 切换到requirements.txt 文件夹下, `pip install -r requirements.txt`


### 代码使用
- 启动：在cmd中输入`python 1-1.py`
- 停止：在cmd中按 `ctrl + c` 或者 手动将鼠标移动到屏幕的角落

### 重要配置
- 炉石传说游戏为全屏
- 分辨率设置1920 x 1080
- 一定要进入佣兵地图后再开启代码
- 每个代码只可以重复刷同一个boss，如果中间需要换地图，可以手动停止代码

## 代码逻辑
前提：
- 默认已经进入地图, 且手动勾选过boss，以及队伍。 如果没有（比如从地图当中退出游戏，或战斗状态中退出，或者断网等），代码不会重新选择boss，以及队伍。此时会出错。
- 请确保网络稳定

### 基本逻辑：
- 战斗前： 一直点击右下角，进入战斗
- 进入战斗
- 战斗结束
    - 没有参加boss战斗，进入地图状态 - 地图上随机点击，选择小奖励并进入下一场战斗
    - 已经参加boss战斗，退出地图状态
- 退出地图状态，等待15秒并选择大奖励
- 重新回到地图，进入战斗前状态

### 脚本逻辑
- 1-1.py
    - 佣兵未上场之前： 一直点击就绪状态
    - 佣兵上场后：
        - 佣兵技能没全部选择时，会从左到右判断哪个佣兵的技能没有选择，并选择
        - 每次选择动作：[右键，右下角左击，佣兵左击，1技能左击，最左边的敌对佣兵左击]
        - 佣兵技能全部选择后，点击就绪，进入战斗
    - 在技能描述处单击15秒，跳过动画
    - 敌方佣兵未死亡， 重新回到佣兵上场后状态
    - 敌方佣兵死亡，回到地图状态
- 2-5.py
    - 佣兵未上场之前： 一直点击就绪状态
    - 佣兵上场后：
        - 佣兵技能没全部选择时，会从左到右判断哪个佣兵的技能没有选择，并选择
        - 每次选择动作：[右键，右下角左击，佣兵左击，1技能左击]
        - 佣兵技能全部选择后，点击就绪，进入战斗
    - 在技能描述处单击15秒，跳过动画
    - 敌方佣兵未死亡， 重新回到佣兵上场后状态
    - 敌方佣兵死亡，回到地图状态
