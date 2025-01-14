import wx
from openai import OpenAI
import threading
import os

# 环境变量中获取 API 密钥
openai_api_key = os.environ.get("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("未在环境变量中找到 API 密钥，请设置 OPENAI_API_KEY。")

# 创建 OpenAI 客户端
client = OpenAI(
    api_key=openai_api_key,
    base_url="https://api.chatanywhere.tech/v1"
)


class TextCtrl(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(TextCtrl, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.text = ""
        self.turns = []
        panel = wx.Panel(self)
        self.panel = panel
        
        # ----------------------------- 标签和输入框 -------------------------------------------
        # 使用 FlexGridSizer 创建布局
        grid_sizer = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        
        theme_label = wx.StaticText(panel, label="主题：")
        # self.theme_input = wx.TextCtrl(panel, size=(550, -1))
        self.theme_input = wx.TextCtrl(panel, size=(550, -1), value="成长")
        
        character_label = wx.StaticText(panel, label="性格：")
        # self.character_input = wx.TextCtrl(panel, size=(550, -1))
        self.character_input = wx.TextCtrl(panel, size=(550, -1), value="自卑，容易犯小错误")
        
        setting_label = wx.StaticText(panel, label="设定：")
        # self.setting_input = wx.TextCtrl(panel, size=(550, -1))
        self.setting_input = wx.TextCtrl(panel, size=(550, -1), value="少女，呆呆的，笨笨的，但很对待事情很用心")
        
        # 将组件添加到 sizer
        grid_sizer.AddMany([
            (theme_label, 0, wx.ALIGN_CENTER_VERTICAL), (self.theme_input, 1, wx.EXPAND),
            (character_label, 0, wx.ALIGN_CENTER_VERTICAL), (self.character_input, 1, wx.EXPAND),
            (setting_label, 0, wx.ALIGN_CENTER_VERTICAL), (self.setting_input, 1, wx.EXPAND),
        ])

        # -------------------------------创建选择菜单 和 按钮 和 输入框-----------------------------------------

        # 选择菜单
        self.content_type = wx.ComboBox(panel, choices=["故事大纲", "章节文本", ], pos=(20, 180))

        # 按钮
        self.generate_button = wx.Button(panel, label="生成")
        self.generate_button.Bind(wx.EVT_BUTTON, self.on_generate)
        
        # 创建右侧输入框，初始隐藏
        self.dynamic_input = wx.TextCtrl(panel, size=(-1, -1))
        self.dynamic_input.SetHint("请输入修改要求...")  # 提示输入
        self.dynamic_input.Hide()  # 隐藏输入框

        # 添加选择菜单和按钮的水平布局
        menu_button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 将选择菜单和按钮添加到水平布局
        menu_button_sizer.Add(self.content_type, flag=wx.EXPAND | wx.RIGHT, border=10)  # 菜单在左，右侧留间距
        menu_button_sizer.Add(self.generate_button, flag=wx.EXPAND | wx.RIGHT, border=10)  # 按钮在中间
        menu_button_sizer.Add(self.dynamic_input, flag=wx.EXPAND, proportion=1)  # 输入框在右，占用剩余空间


        # ------------------------------------- 结果显示框  -----------------------------------
        self.result_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(400, 200))


        # -------------------------------------  总布局  -------------------------------------
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(grid_sizer, flag=wx.ALL, border=10)
        main_sizer.Add(menu_button_sizer, flag=wx.ALL | wx.EXPAND, border=10)  # 水平布局加入主布局
        main_sizer.Add(self.result_text, flag=wx.ALL | wx.EXPAND, border=10, proportion=1)

        panel.SetSizer(main_sizer)

        # 窗口设置
        self.SetSize(1540, 800)
        self.SetTitle("Inspiration")
        self.Centre()
        self.Show(True)

    def start_thread(self):
        # 检查是否选择功能菜单
        selected_function = self.content_type.GetValue()
        if not selected_function:  # 未选择功能
            wx.MessageBox("请选择一个功能菜单！", "错误", wx.OK | wx.ICON_ERROR)
            return
        
        # 根据功能选择设置提示词
        if selected_function == "故事大纲":
            self.text = "你是一个创意写作助手，请根据以下设定生成一个完整的故事大纲。大纲需要包含以下要素：\
                        1. 故事背景（时间、地点、主要设定）。\
                        2. 主要角色及其性格特点。\
                        3. 故事的主要冲突或问题。\
                        4. 故事的关键情节节点（包括开端、发展、高潮、结局）。\
                        请确保大纲内容具体、条理清晰、富有创意，并能够为写作者提供清晰的方向。文章风格可根据设定进行调整，字数不少于300字。\
                        （仅仅回复大纲，无需额外的文字）"
                        
        elif selected_function == "章节文本":
            self.text = "你是一个专业写作助手，请根据下面的设定撰写故事的一个章节。\
                        章节需包含生动的描述、细腻的情感刻画，以及扣人心弦的情节发展，\
                        字数不少于500字。（仅仅回复章节文本，无需额外的文字）"

        # 启动线程进行内容生成
        thread = threading.Thread(target=self.create_completion, args=())
        thread.start()

    def create_completion(self):
        self.generate_button.SetLabel("请等待...")

        # 获取用户输入
        theme = self.theme_input.GetValue()
        character = self.character_input.GetValue()
        setting = self.setting_input.GetValue()

        user_input = f"主题：{theme}\n角色：{character}\n设定：{setting}"

        # 构建 messages 列表
        messages = [
            {"role": "system", "content": self.text},
            {"role": "user", "content": user_input}
        ]

        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.9,
                max_tokens=2500,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.6,
                stream=True, # 启用流式响应
            )

            self.turns.append(f"\n{user_input}\n")
            self.turns.append("\n")
            
            # 显示用户的输入
            # wx.CallAfter(self.result_text.SetValue, "".join(self.turns))  

            for chunk in completion:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content is not None:  # 判断属性和内容是否存在
                    content = delta.content
                    for char in content:
                        self.turns[-1] += char
                        # wx.CallAfter(self.result_text.SetValue, "".join(self.turns))
                        wx.CallAfter(self.result_text.SetValue, "".join(self.turns[-1]))
       
        except Exception as e:
            print("发生错误：{str(e)}")
            # wx.CallAfter(self.result_text.SetValue, f"发生错误：{str(e)}")
            

        finally:
            self.generate_button.SetLabel("修改")
            self.dynamic_input.SetValue("")  # 清空输入框
            
            # 显示动态输入框
            wx.CallAfter(self.dynamic_input.Show)
            
            # 聚焦到输入框 (闪退 弃用)
            # self.dynamic_input.SetFocus()  
            
            # 刷新布局
            wx.CallAfter(self.panel.Layout)  

        # 仅保留最近的 10 条对话记录
        if len(self.turns) <= 10:
            self.text = "".join(self.turns)
        else:
            self.text = "".join(self.turns[-10:])

    # 输入内容为空时禁止提交（弹出提示）
    def on_generate(self, event):
        if self.theme_input.GetValue() == "" or self.character_input.GetValue() == "" or self.setting_input.GetValue() == "":
            toastone = wx.MessageDialog(None, "请输入内容", "提示", wx.YES_DEFAULT)
            if toastone.ShowModal() == wx.ID_YES:
                toastone.Destroy()
            return

        self.result_text.SetValue(self.text)
        self.start_thread()


def main():
    app = wx.App(False)
    TextCtrl(None)
    app.MainLoop()


if __name__ == "__main__":
    main()
