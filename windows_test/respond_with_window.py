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
        self.tex = wx.TextCtrl(panel, id=wx.ID_ANY, pos=(20, 20), size=(400, -1))
        self.button = wx.Button(panel, -1, u"提交", pos=(435, 20))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        self.text1 = wx.TextCtrl(panel, pos=(20, 60), size=(500, 400), style=wx.TE_MULTILINE)
        self.SetSize(540, 500)
        self.SetTitle("Ai讲故事")
        self.Centre()
        self.Show(True)

    def start_thread(self):
        thread = threading.Thread(target=self.create_completion, args=())
        thread.start()

    def create_completion(self):
        self.button.SetLabel("请等待...")
        user_input = self.tex.GetValue()

        # 构建 messages 列表
        messages = [
            {"role": "system", "content": self.text},
            {"role": "user", "content": user_input}
        ]

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.9,
            max_tokens=2500,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6
        )
        ai_response = completion.choices[0].message.content + "\n\n"

        # 更新对话记录
        self.turns.append(f"用户：{user_input}")
        self.turns.append(f"\nAI：{ai_response}")

        print(self.turns)

        self.button.SetLabel("提交")

        # 仅保留 10 条对话记录
        if len(self.turns) <= 10:
            self.text = "".join(self.turns)
        else:
            self.text = "".join(self.turns[-10:])
        
        wx.CallAfter(self.text1.SetValue, self.text)  # 使用 CallAfter 确保 UI 更新在主线程中进行

    # 输入内容为空时禁止提交（弹出提示）
    def OnClick(self, event):
        if self.tex.GetValue() == "":
            toastone = wx.MessageDialog(None, "请输入内容", "提示", wx.YES_DEFAULT)
            if toastone.ShowModal() == wx.ID_YES:
                toastone.Destroy()
            return

        self.text1.SetValue(self.text)
        self.start_thread()

def main():
    app = wx.App(False)
    TextCtrl(None)
    app.MainLoop()

if __name__ == "__main__":
    main()