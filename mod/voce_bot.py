from config import *
from mod.connect_openai import *
import requests
from mod.mongo_model import *
import time
import sys
import logging

# 日志
logging.basicConfig(format='%(asctime)s %(message)s', filename = os.path.join(os.getcwd(),'log.txt'), level=logging.INFO)

dbname = "test"

# 数据连接
Current_Chat_Mode = PymongoCRUD(dbname, "current_chat_mode")
Current_Ai_System = PymongoCRUD(dbname, "current_ai_system")
Voce_Display_Msg = PymongoCRUD(dbname, "voce_display_msg")
Server_Store_System_Mode = PymongoCRUD(dbname, "server_store_system_mode")


command_help = "/help"
command_context_mode = "/context"
command_single_mode = "/single"
command_clean_msg = "/clean"
command_check_msg = "/check"
command_view_system = "/view"

voce_help = {
    command_help: "调出帮助菜单",
    command_context_mode: "设置为上下文聊天模式，默认为单次聊天模式，运行这个命令可以开启上下文聊天，"
                          "上下文聊天会保存聊天记录，若不想影响后续聊天，请手动清除聊天记录",
    command_single_mode: "设置为单次聊天模式",
    command_clean_msg: "清除与AI的聊天记录",
    command_check_msg: "查看与AI的聊天记录",
    command_view_system: "查看如何为AI赋予一个角色"
}

command_show_server_system = "/show"
command_set_system = "/set+"
command_select_system = "/select+"
command_show_me_system = "/me"
command_clean_me_system = "/unset"

voce_ai_system_help = {
    command_show_server_system:  f"通过输入 {command_show_server_system} 可以显示已经存储备用的角色",
    command_show_me_system: f"通过输入 {command_show_me_system} 可以查看我已经设置的角色",
    command_set_system: f"通过输入 {command_set_system}内容 来设置行为,例如:{command_set_system}角色描述(描述可以参考系统预制的格式)",
    command_select_system: f"通过输入 {command_select_system}角色 来选择一个角色(必须是系统有的), 例如：/select+程序员",
    command_clean_me_system: f"通过输入 {command_clean_me_system} 可以清除已经设置的行为，清除聊天记录的时候会同时清除角色"
}

# 隐藏命令
# /admin+角色名+角色描述
command_admin_set_system = "/admin+"

chat_mod_descript = {
    "0": "单聊天模式",
    "1": "上下文模式"
}


class MongDBManger:
    def __init__(self, user_id):
        self.current_user_id = user_id
        # 当前聊天模式： 0单聊天 | 1上下文 
        self.current_chat_mode = Current_Chat_Mode
        # AI行为设置
        self.current_ai_system = Current_Ai_System
        # 用于上下文聊天
        self.user_voce_display_msg = Voce_Display_Msg
        # 系统S存储的模型
        self.server_store_system_mode = Server_Store_System_Mode
        #
        self.migrate_user_current_chat_mode()

    # 聊天模式的操作
    def migrate_user_current_chat_mode(self):
        # 当前聊天模式，如果不存在就插入;
        if not self.current_chat_mode.find_one({"user": self.current_user_id}):
            self.current_chat_mode.insert_one({'user': self.current_user_id, 'model': "0"})

    def update_user_current_chat_mode(self, chat_mode):
        # 当前聊天模式，如果不存在就插入;
        filter_data = {"user": self.current_user_id}
        update_data = {"user": self.current_user_id, "model": chat_mode}
        self.current_chat_mode.update_one(filter_data, update_data)

    def find_user_current_chat_mode(self):
        find_data = {"user": self.current_user_id}
        return self.current_chat_mode.find_one(find_data)

    # 聊天记录
    def find_user_current_voce_display_msg_one(self, created_at):
        find_data = {"created_at": created_at, "user": self.current_user_id}
        return self.user_voce_display_msg.find_one(find_data)

    def insert_user_current_voce_display_msg(self, created_at, user, role, msg):
        insert_data = {
            "created_at": created_at,
            "user": user,
            "role": role,
            "msg": msg
        }
        self.user_voce_display_msg.insert_one(insert_data)

    def find_user_current_voce_display_msg_all(self):
        find_data = {"user": self.current_user_id}
        return self.user_voce_display_msg.find_many(find_data)
    
    def delete_user_current_voce_display_msg_one(self, created_at):
        find_data = {"created_at": created_at, "user": self.current_user_id}
        return self.user_voce_display_msg.delete_one(find_data)
    
    def delete_user_current_voce_display_msg_many(self):
        find_data = {"user": self.current_user_id}
        return self.user_voce_display_msg.delete_many(find_data)

    # AI行为设置
    def find_user_current_ai_system(self):
        find_data = {"user": self.current_user_id}
        return self.current_ai_system.find_one(find_data)

    def set_user_current_ai_system(self, ai_system):
        # 当前聊天模式，如果不存在就插入;
        if not self.current_ai_system.find_one({"user": self.current_user_id}):
            self.insert_user_current_ai_system(ai_system)   
        else:
            self.update_user_current_ai_system(ai_system)

    def insert_user_current_ai_system(self, ai_system):
        insert_data = {
            "user": self.current_user_id,
            "ai_system": ai_system
        }
        self.current_ai_system.insert_one(insert_data)

    def update_user_current_ai_system(self, ai_system):
        # 当前聊天模式，如果不存在就插入;
        filter_data = {"user": self.current_user_id}
        update_data = {"user": self.current_user_id, "ai_system": ai_system}
        self.current_ai_system.update_one(filter_data, update_data)
        
    def delete_user_current_ai_system_one(self):
        find_data = {"user": self.current_user_id}
        return self.current_ai_system.delete_many(find_data)
    
    # 服务器预制的AI_system,服务器角色库
    def find_server_store_system_mode_all(self):
        return self.server_store_system_mode.find_all()
    
    def find_server_store_system_mode_one(self, ai_system_name):
        find_data = {"ai_system_name": ai_system_name}
        return self.server_store_system_mode.find_one(find_data)
            
    # # 隐藏功能,向服务器写入一个角色描述
    def set_server_store_system_mode(self, ai_system):
        # 当前聊天模式，如果不存在就插入;
        if not self.server_store_system_mode.find_one({"ai_system_name": ai_system[1]}):
            self.insert_server_store_system_mode(ai_system)   
        else:
            self.update_server_store_system_mode(ai_system)

    def insert_server_store_system_mode(self, ai_system):
        insert_data = {
            "ai_system_name": ai_system[1],
            "ai_system_descript": ai_system[2].replace("\n", ""),
        }
        self.server_store_system_mode.insert_one(insert_data)

    def update_server_store_system_mode(self, ai_system):
        # 当前聊天模式，如果不存在就插入;
        filter_data = {"ai_system_name": ai_system[1]}
        update_data = {"ai_system_name": ai_system[1], "ai_system_descript": ai_system[2].replace("\n", "")}
        self.server_store_system_mode.update_one(filter_data, update_data)


class MessageHandler:
    def __init__(self, data):
        self.data = data
        self.user_id = str(self.data.from_uid)
        self.created_at = self.data.created_at
        self.target_gid = self.data.target.gid
        self.msg = self.data.detail.content
        self.mongo_manager = MongDBManger(self.user_id)

    def handle(self):
        # 如果是群发消息，不接收
        sys.stdout = open('message_handler.log', 'a')
        print(f"执行到5 {time.time()}")
        if self.is_group_message():
            return
        # 不处理bot的msg
        if self.is_bot_message():
            return
        # 功能函数
        # 帮助
        if self.is_help_command():
            return self.send_help()
        # 切换聊天模式
        if self.is_switch_context_mode_command():
            return self.switch_chat_mode("1")
        if self.is_switch_single_chat_mode_command():
            return self.switch_chat_mode("0")
        # 聊天记录操作
        if self.is_clear_chat_history_command():
            return self.clear_chat_history()
        if self.is_view_chat_history_command():
            return self.view_chat_history()
        if self.is_view_server_store_ai_system():
            return self.view_server_store_ai_system()
        
        # system设置操作
        if self.is_view_ai_system_help():
            return self.send_ai_system_help()
        if self.is_clear_user_ai_system():
            return self.clear_user_ai_system()
        if self.is_set_user_ai_system():
            return self.set_user_ai_system()
        if self.is_view_user_current_ai_system():
            return self.view_user_current_ai_system()
        if self.is_select_server_store_ai_system_to_user():
            return self.select_server_store_ai_system_to_user()
        
        # 隐藏命令
        if self.is_admin_set_ai_system():
            return self.admin_set_ai_system()
        
        # 是否命令输入错误
        if self.is_command_wrong():
            return self.command_wrong()

        # 重复消息晒出
        if self.mongo_manager.find_user_current_voce_display_msg_one(self.created_at):
            return
        else:
            self.mongo_manager.insert_user_current_voce_display_msg(self.created_at, self.user_id, "user", self.msg)

        return self.process_user_message()
    
    def is_group_message(self):
        return self.target_gid is not None

    def is_bot_message(self):
        return self.user_id == Settings.VoceChat['bot_id']

    # 帮助
    def is_help_command(self):
        return self.msg == command_help
    
    def send_help(self):
        chat_mod_id = self.get_user_current_chat_mode()
        chat_mod_id_text = chat_mod_descript[str(chat_mod_id)]
        help_text = f"|命令|功能|\n|-|-|\n |当前模式|你的模式为:{chat_mod_id_text};|"
        for name, descript in voce_help.items():
            help_text += f"|{name}|{descript}|\n"
        return self.send_to_voce_bot(f"### 功能展示\n{help_text}")

    # 切换模式
    def is_switch_context_mode_command(self):
        return command_context_mode in self.msg[:len(command_context_mode)+1]

    def is_switch_single_chat_mode_command(self):
        return command_single_mode in self.msg[:len(command_context_mode)+1]
    
    def switch_chat_mode(self, chat_mod):
        self.mongo_manager.update_user_current_chat_mode(chat_mod)
        chat_mod_id = self.get_user_current_chat_mode()
        chat_mod_id_text = chat_mod_descript[str(chat_mod_id)]
        return self.send_to_voce_bot(f"修改成功,当前模式为{chat_mod_id_text}")
    
    # 聊天记录
    def is_clear_chat_history_command(self):
        return command_clean_msg in self.msg[:len(command_context_mode)+1]
    
    def clear_chat_history(self):
        self.mongo_manager.delete_user_current_voce_display_msg_many()
        return self.send_to_voce_bot("聊天记录清理成功")
    
    def is_view_chat_history_command(self):
        return command_check_msg in self.msg[:len(command_context_mode)+1]
    
    def view_chat_history(self):
        history_msg = self.process_user_history_msg()
        return self.send_to_voce_bot(str(history_msg))

    # AI System 设置
    def is_view_ai_system_help(self):
        return command_view_system in self.msg[:len(command_view_system)+1]
    
    def send_ai_system_help(self):
        user_ai_system = "未设置"
        if self.get_user_current_ai_system():
            user_ai_system = self.get_user_current_ai_system()
        help_text = f"|命令|功能|\n|-|-|\n |当前模式|你设置的AI角色:{user_ai_system};|\n"
        for name, descript in voce_ai_system_help.items():
            help_text += f"|{name}|{descript}|\n"
        return self.send_to_voce_bot(f"### AI角色设置帮助\n{help_text}")

    def is_clear_user_ai_system(self):
        return command_clean_me_system in self.msg[:len(command_clean_me_system)+1]
    
    def clear_user_ai_system(self):
        self.mongo_manager.delete_user_current_ai_system_one()
        return self.send_to_voce_bot("角色设置清除成功")

    def is_set_user_ai_system(self):
        return command_set_system in self.msg[:len(command_set_system)+1]

    def set_user_ai_system(self):
        ai_system = self.msg.split("+")
        self.mongo_manager.set_user_current_ai_system(ai_system[1].replace("\n", ""))
        return self.send_to_voce_bot(f"角色设置成功")

    def is_view_server_store_ai_system(self):
        return command_show_server_system in self.msg[:len(command_show_server_system)+1]

    def view_server_store_ai_system(self):
        help_text = f"|角色名称|角色描述|\n|-|-|\n"
        if self.get_server_current_ai_system():
            server_store_ai_system = self.get_server_current_ai_system()
            for i in server_store_ai_system:
                help_text += f"|{i['ai_system_name']}|{i['ai_system_descript']}|\n"
            return self.send_to_voce_bot(f"### 系统预设角色\n{help_text}")
        return self.send_to_voce_bot(f"系统无预设角色")
            
    # 查看我的角色
    def is_view_user_current_ai_system(self):
        return command_show_me_system in self.msg[:len(command_show_me_system)+1]

    def view_user_current_ai_system(self):
        user_ai_system = "未设置"
        if self.get_user_current_ai_system():
            user_ai_system = self.get_user_current_ai_system()
        return self.send_to_voce_bot(f"### 当前AI角色设置为\n{user_ai_system}")

    # 选择一个服务器预设的角色
    def is_select_server_store_ai_system_to_user(self):
        return command_select_system in self.msg[:len(command_select_system)+1]

    def select_server_store_ai_system_to_user(self):
        ai_system = self.msg.split("+")
        if not self.mongo_manager.find_server_store_system_mode_one(ai_system[1]):
            return self.send_to_voce_bot(f"没有预制该角色")
        ai_system_find = self.mongo_manager.find_server_store_system_mode_one(ai_system[1])
        self.mongo_manager.set_user_current_ai_system(ai_system_find["ai_system_descript"])
        return self.send_to_voce_bot(f"设置{ai_system_find['ai_system_name']}成功")

    # 隐藏命令,用来给服务器插入一个预设角色
    def is_admin_set_ai_system(self):
        return command_admin_set_system in self.msg[:len(command_admin_set_system)+1]

    def admin_set_ai_system(self):
        ai_system = self.msg.split("+")
        self.mongo_manager.set_server_store_system_mode(ai_system)
        return self.send_to_voce_bot("设置成功!")

    # 是否输入错误
    def is_command_wrong(self):
        return r"/" in self.msg.replace("\n", "")[:3]
    
    def command_wrong(self):
        return self.send_to_voce_bot("命令输入错误,请检查!")

    # 开始处理对话
    def process_user_message(self):
        send_msg = []
        ai_mod = self.get_user_current_ai_system()
        if ai_mod:
            send_msg.insert(0, {'role': 'system', 'content': ai_mod})

        # user_current_chat_mode = self.mongo_manager.find_user_current_chat_mode()
        if self.get_user_current_chat_mode() == "1":
            history_msg = self.process_user_history_msg()
            if len(history_msg) > 0:
                send_msg += history_msg
            send_msg.append({'role': "user", 'content': self.msg})
            logging.info(send_msg)
            response = send_msg_to_openai(send_msg)
        else:
            send_msg.append({'role': "user", 'content': self.msg})
            logging.info(send_msg)
            response = send_msg_to_openai(send_msg)

        if response != "超时错误，请重试！":
            if self.get_user_current_chat_mode() == "1":
                self.mongo_manager.insert_user_current_voce_display_msg(
                    self.created_at, self.user_id, "assistant", response)
            return self.send_to_voce_bot(response)
        self.mongo_manager.delete_user_current_voce_display_msg_one(self.created_at)
        return self.send_to_voce_bot(response)
    
    # 功能性函数
    # 获取当前用户的聊天模式
    def get_user_current_chat_mode(self):
        user_current_ai_system = self.mongo_manager.find_user_current_chat_mode()
        if not user_current_ai_system:
            return
        return user_current_ai_system["model"]

    # 获取当前用户的ai system角色设置
    def get_user_current_ai_system(self):
        user_current_ai_system = self.mongo_manager.find_user_current_ai_system()
        if not user_current_ai_system:
            return
        return user_current_ai_system["ai_system"]

    # 获取当期服务器中的角色情况
    def get_server_current_ai_system(self):
        return self.mongo_manager.find_server_store_system_mode_all()

    # 处理历史聊天记录
    def process_user_history_msg(self):
        find_msg = self.mongo_manager.find_user_current_voce_display_msg_all()
        history_msg_list = []
        for i in find_msg:
            history_msg_list.append({"role": i["role"], "content": i["msg"]})
        return history_msg_list

    # 向voce_chat_bot回传消息
    def send_to_voce_bot(self, message):
        headers = {'content-type': "text/markdown", 'x-api-key': Settings.VoceChat['secret']}
        url = f"{Settings.VoceChat['url']}/api/bot/{Settings.VoceChat['sent_to']}/{self.user_id}"
        requests.post(url=url, headers=headers, data=message.encode('utf-8'))
