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
        
        # ----------------------------- 标签和输入框 -------------------------------------------
        # 使用 FlexGridSizer 创建布局
        grid_sizer = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        
        theme_label = wx.StaticText(panel, label="主题：")
        self.theme_input = wx.TextCtrl(panel, size=(550, -1))
        
        character_label = wx.StaticText(panel, label="性格：")
        self.character_input = wx.TextCtrl(panel, size=(550, -1))
        
        setting_label = wx.StaticText(panel, label="设定：")
        self.setting_input = wx.TextCtrl(panel, size=(550, -1))
        
        # 将组件添加到 sizer
        grid_sizer.AddMany([
            (theme_label, 0, wx.ALIGN_CENTER_VERTICAL), (self.theme_input, 1, wx.EXPAND),
            (character_label, 0, wx.ALIGN_CENTER_VERTICAL), (self.character_input, 1, wx.EXPAND),
            (setting_label, 0, wx.ALIGN_CENTER_VERTICAL), (self.setting_input, 1, wx.EXPAND),
        ])

        # -------------------------------创建选择菜单 和 按钮-----------------------------------------

        # 选择菜单
        self.content_type = wx.ComboBox(panel, choices=["故事大纲", "章节文本", ], pos=(20, 180))

        # 按钮
        self.generate_button = wx.Button(panel, label="生成")
        self.generate_button.Bind(wx.EVT_BUTTON, self.on_generate)

        # 添加选择菜单和按钮的水平布局
        menu_button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 将选择菜单和按钮添加到水平布局
        menu_button_sizer.Add(self.content_type, flag=wx.EXPAND | wx.RIGHT, border=10)  # 菜单在左，右侧留间距
        menu_button_sizer.Add(self.generate_button, flag=wx.EXPAND)  # 按钮在右，占用剩余空间


        # ------------------------------------- 结果显示框  -----------------------------------
        self.result_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(400, 200))


        # -------------------------------------  总布局  -------------------------------------
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(grid_sizer, flag=wx.ALL, border=10)
        main_sizer.Add(menu_button_sizer, flag=wx.ALL | wx.EXPAND, border=10)  # 水平布局加入主布局
        main_sizer.Add(self.result_text, flag=wx.ALL | wx.EXPAND, border=10, proportion=1)

        panel.SetSizer(main_sizer)

        # 窗口设置
        self.SetSize(640, 500)
        self.SetTitle("Inspiration")
        self.Centre()
        self.Show(True)

    def start_thread(self):
        thread = threading.Thread(target=self.create_completion, args=())
        thread.start()

    def create_completion(self):
        self.generate_button.SetLabel("请等待...")
        user_input = self.tex.GetValue()

        # 获取用户输入
        theme = self.theme_input.GetValue()
        character = self.character_input.GetValue()
        setting = self.setting_input.GetValue()

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

            self.turns.append(f"\n用户：{user_input}\n")
            self.turns.append("\nAI：")
            wx.CallAfter(self.result_text.SetValue, "".join(self.turns))  # 先显示用户的输入

            for chunk in completion:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content is not None:  # 判断属性和内容是否存在
                    content = delta.content
                    for char in content:
                        self.turns[-1] += char
                        wx.CallAfter(self.result_text.SetValue, "".join(self.turns))
       
        except Exception as e:
            wx.CallAfter(self.result_text.SetValue, f"发生错误：{str(e)}")

        finally:
            self.button.SetLabel("提交")

        # 仅保留最近的 10 条对话记录
        if len(self.turns) <= 10:
            self.text = "".join(self.turns)
        else:
            self.text = "".join(self.turns[-10:])

    # 输入内容为空时禁止提交（弹出提示）
    def on_generate(self, event):
        if self.tex.GetValue() == "":
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
