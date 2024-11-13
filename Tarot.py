import os  
import random  
import time  
import plugins  
from bridge.context import ContextType  
from bridge.reply import Reply, ReplyType  
from common.log import logger 
from plugins import *  
from PIL import Image, ImageDraw  


@plugins.register(  
    name="Tarot",  # 插件名称  
    desire_priority=99,  # 插件优先级  
    hidden=False,  # 是否隐藏  
    desc="塔罗牌",  # 插件描述  
    version="1.0",  # 插件版本  
    author="sakura7301",  # 作者  
)  
class Tarot(Plugin):  
    def __init__(self):  
        super().__init__()  # 调用父类的初始化 
        self.CARDS_DIR =  "./plugins/Tarot/image"     # 定义塔罗牌目录  
        self.OUTPUT_DIR = "./plugins/Tarot/temp"  # 定义输出目录  
        self.delete_all_files_in_directory(self.OUTPUT_DIR)
        # 注册处理上下文的事件  
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context  
        logger.info("[Tarot] 插件初始化完毕")  

    def delete_all_files_in_directory(self, directory):  
        """删除指定目录下的所有文件"""  
        if not os.path.exists(directory):  
            logger.warning(f"目录不存在: {directory}")  
            return "目录不存在"  # 返回特定消息  

        try:  
            # 遍历目录中的所有文件和子目录  
            for filename in os.listdir(directory):  
                file_path = os.path.join(directory, filename)  
                # 检查是否是文件  
                if os.path.isfile(file_path):  
                    os.remove(file_path)  # 删除文件  
                    logger.info(f"已清除文件: {file_path}")  
        except Exception as e:  
            logger.error(f"发生错误: {e}")   

    def ensure_directory_exists(self, directory):  
        """检查指定目录是否存在，如果不存在则创建该目录"""  
        try:  
            if not os.path.exists(directory):  
                os.makedirs(directory)  # 创建目录  
                logger.info(f"目录已创建: {directory}")  
            else:  
                logger.debug(f"目录已存在: {directory}")  
        except Exception as e:  
            logger.error(f"发生错误: {e}")  

    def shuffle_cards(self):  
        """随机洗牌并返回卡牌列表"""  
        logger.debug("开始洗牌...")  
        card_files = os.listdir(self.CARDS_DIR)  
        random.shuffle(card_files)  
        logger.debug("洗牌完成！")  
        return card_files  

    def generate_draw_flag(self):  
        """生成随机的抽牌标志 (0: 逆位, 1: 正位)"""  
        random.seed(time.time())  
        return random.randint(0, 1)  

    def get_card_name(self, card_file):  
        """根据文件名获取塔罗牌名称"""  
        return card_file.split('_', 1)[1].replace('.jpg', '')  

    def TarotSingleCardRequest(self, query):  
        # 定义占卜关键词列表  
        divination_keywords = ['抽牌', '抽一张牌']  
        return any(keyword in query for keyword in divination_keywords)  

    def TarotThreeCardsRequest(self, query):  
        # 定义占卜关键词列表  
        divination_keywords = ['三牌阵','三张牌阵','过去-现在-未来阵']  
        return any(keyword in query for keyword in divination_keywords)  

    def TarotCrossCardsRequest(self, query):  
        # 定义占卜关键词列表  
        divination_keywords = ['凯尔特十字','凯尔特十字牌阵','十字牌阵','十字阵']  
        return any(keyword in query for keyword in divination_keywords)  

    def TarotSingleCard(self, m=None):  
        """抽取单张塔罗牌，支持指定牌位"""  
        card_files = self.shuffle_cards()  
        draw_flag = self.generate_draw_flag()  # 生成抽牌标志  

        output_filename = "Single"  

        # 如果指定了牌位  
        if m is not None:  
            if 0 <= m < len(card_files):  
                selected_card = card_files[m]  
                card_name = self.get_card_name(selected_card)  
                logger.debug(f"抽取的牌为: {card_name} (标志: {draw_flag})")  
            else:  
                logger.info("参数m超出范围，使用随机数抽取牌")  
                selected_card = card_files[random.randint(0, len(card_files) - 1)]  
                card_name = self.get_card_name(selected_card)  
                logger.debug(f"抽取的牌为: {card_name} (标志: {draw_flag})")  
        else:  
            selected_card = card_files[random.randint(0, len(card_files) - 1)]  
            card_name = self.get_card_name(selected_card)  
            logger.info(f"抽取的牌为: {card_name} (标志: {draw_flag})")  
        

        # 根据抽牌标志处理图像  
        if draw_flag == 0:  # 逆位处理  
            logger.debug(f"抽到：{card_name}(逆位)")  
            output_filename += f"_{card_name}逆"  
        else:  
            logger.debug(f"抽到：{card_name}(正位)")  
            output_filename += f"_{card_name}正"  
        
        # 生成路径  
        output_filename += ".png"  
        # 检查目录是否存在
        self.ensure_directory_exists(self.OUTPUT_DIR)
        # 生成路径
        output_path = os.path.join(self.OUTPUT_DIR, output_filename)   

        # 检查文件是否已存在  
        if os.path.exists(output_path):  
            #存在就直接返回  
            logger.debug(f"找到已存在的图片：{output_path}")   
        else:  
            card_path = os.path.join(self.CARDS_DIR, selected_card)  
            card_image = Image.open(card_path).convert("RGBA")  

            if draw_flag == 0:  
                # 逆位处理  
                card_image = card_image.transpose(Image.FLIP_TOP_BOTTOM)  # 反转图像   

            # 压缩图像  
            card_image = card_image.resize((card_image.width//3, card_image.height//3), Image.LANCZOS)  

            # 保存合成的图片   
            card_image.save(output_path)  

        return open(output_path, 'rb')  

    def TarotThreeCards(self, query=None):  
        """抽取三张塔罗牌并生成合成图像"""  
        # 洗牌  
        card_files = self.shuffle_cards()  
        selected_cards = []  # 用于保存选中的卡牌信息  
        output_filename = "Three"  

        for i in range(3):  
            draw_flag = self.generate_draw_flag()  # 生成抽牌标志  
            #按顺序抽  
            selected_card = card_files[i]  
            card_name = self.get_card_name(selected_card)  
            selected_cards.append((selected_card, card_name, draw_flag))  # 保存完整信息  
            
            if draw_flag == 0:  # 逆位处理  
                logger.debug(f"抽到：{card_name}(逆位)")  
                output_filename += f"_{card_name}逆"  
            else:  
                logger.debug(f"抽到：{card_name}(正位)")  
                output_filename += f"_{card_name}正"  

        logger.info("抽取的三张牌为: " + ", ".join([f"{name}({'正位' if flag == 1 else '逆位'})" for _, name, flag in selected_cards]))  

        # 生成路径  
        output_filename += ".png"  
        # 检查目录是否存在
        self.ensure_directory_exists(self.OUTPUT_DIR)
        # 生成路径
        output_path = os.path.join(self.OUTPUT_DIR, output_filename)   

        # 检查文件是否已存在  
        if os.path.exists(output_path):  
            #存在就直接返回  
            logger.debug(f"找到已存在的图片：{output_path}")   
        else:  
            # 生成合成图像逻辑  
            card_images = []  
            
            for selected_card, card_name, draw_flag in selected_cards:  
                card_path = os.path.join(self.CARDS_DIR, selected_card)  
                card_image = Image.open(card_path).convert("RGBA")  
                
                # 根据抽牌标志处理图像  
                if draw_flag == 0:  # 逆位处理  
                    card_image = card_image.transpose(Image.FLIP_TOP_BOTTOM)  # 反转图像  
                
                card_images.append(card_image)  # 添加处理后的图像  

            total_width = sum(img.width for img in card_images) + 100  # 3张牌的宽度加上间隔  
            total_height = max(img.height for img in card_images) + 20  # 适当增加高度  
            background_color = (200, 220, 255)  # 背景颜色  
            new_image = Image.new('RGBA', (total_width, total_height), background_color)  

            draw = ImageDraw.Draw(new_image)  
            border_color = (0, 0, 0)  # 边框颜色  
            border_thickness = 3  

            # 将三张牌放入新图片  
            x_offset = 20  
            for img in card_images:  
                new_image.paste(img, (x_offset, 10))  
                draw.rectangle([x_offset, 10, x_offset + img.width, 10 + img.height], outline=border_color, width=border_thickness)  
                x_offset += img.width + 30  

            # 压缩图像  
            new_image = new_image.resize((total_width//5, total_height//5), Image.LANCZOS)  

            # 保存合成的图片  
            new_image.save(output_path)  

            logger.debug(f"合成的三张牌图片已保存: {output_path}")  
        return open(output_path, 'rb')  

    def TarotCrossCards(self, query=None):  
        """抽取十张塔罗牌并生成合成图像"""  
        # 洗牌  
        card_files = self.shuffle_cards()  
        selected_cards = []  

        output_filename = "Cross"  

        for i in range(5):  
            draw_flag = self.generate_draw_flag()  # 生成抽牌标志  
            #按顺序抽  
            selected_card = card_files[i]  
            card_name = self.get_card_name(selected_card)  
            selected_cards.append((selected_card, card_name, draw_flag))  # 保存完整信息   
            
            if draw_flag == 0:  # 逆位处理  
                logger.debug(f"抽到：{card_name}(逆位)")  
                output_filename += f"_{card_name}逆"  
            else:  
                logger.debug(f"抽到：{card_name}(正位)")  
                output_filename += f"_{card_name}正"  

        logger.info("抽取的五张牌为: " + ", ".join([f"{name}({'正位' if flag == 1 else '逆位'})" for _, name, flag in selected_cards]))  

        # 生成路径  
        output_filename += ".png"  
        # 检查目录是否存在
        self.ensure_directory_exists(self.OUTPUT_DIR)
        # 生成路径
        output_path = os.path.join(self.OUTPUT_DIR, output_filename)   

        # 检查文件是否已存在  
        if os.path.exists(output_path):  
            #存在就直接返回  
            logger.debug(f"找到已存在的图片：{output_path}")   
        else:  
            card_images = []  
            
            for selected_card, card_name, draw_flag in selected_cards:  
                card_path = os.path.join(self.CARDS_DIR, selected_card)  
                card_image = Image.open(card_path).convert("RGBA")  
                
                # 根据抽牌标志处理图像  
                if draw_flag == 0:  # 逆位处理  
                    card_image = card_image.transpose(Image.FLIP_TOP_BOTTOM)  # 反转图像  
                    
                card_images.append(card_image)  # 添加处理后的图像  
            
            card_width, card_height = card_images[0].size  
            total_width = card_width * 3 + 120  
            total_height = card_height * 3 + 120  

            # 创建新图像  
            background_color = (200, 220, 255)  
            new_image = Image.new('RGBA', (total_width, total_height), background_color)  
            draw = ImageDraw.Draw(new_image)  
            
            border_color = (0, 0, 0)  
            border_thickness = 3  

            center_x = (total_width - card_width) // 2  
            center_y = (total_height - card_height) // 2  

            # 中心  
            new_image.paste(card_images[0], (center_x, center_y))  
            draw.rectangle([center_x, center_y, center_x + card_width, center_y + card_height], outline=border_color, width=border_thickness)  

            # 上方  
            new_image.paste(card_images[1], (center_x, center_y - card_height - 30))  
            draw.rectangle([center_x, center_y - card_height - 30, center_x + card_width, center_y - 30], outline=border_color, width=border_thickness)  

            # 下方  
            new_image.paste(card_images[2], (center_x, center_y + card_height + 30))  
            draw.rectangle([center_x, center_y + card_height + 30, center_x + card_width, center_y + card_height * 2 + 30], outline=border_color, width=border_thickness)  

            # 左侧  
            new_image.paste(card_images[3], (center_x - card_width - 30, center_y))  
            draw.rectangle([center_x - card_width - 30, center_y, center_x - 30, center_y + card_height], outline=border_color, width=border_thickness)  

            # 右侧  
            new_image.paste(card_images[4], (center_x + card_width + 30, center_y))  
            draw.rectangle([center_x + card_width + 30, center_y, center_x + card_width * 2 + 30, center_y + card_height], outline=border_color, width=border_thickness)  

            # 压缩图像  
            new_image = new_image.resize((total_width//5, total_height//5), Image.LANCZOS)  

            # 保存合成的图片  
            new_image.save(output_path)  

            logger.debug(f"合成的五张牌图片已保存: {output_path}")  
        return open(output_path, 'rb')  

    def on_handle_context(self, e_context: EventContext):  
        """处理上下文事件"""  
        if e_context["context"].type not in [ContextType.TEXT]:  
            logger.debug("[Tarot] 上下文类型不是文本，无需处理")  
            return  
        
        content = e_context["context"].content.strip()  
        logger.debug(f"[Tarot] 处理上下文内容: {content}")  

        if self.TarotSingleCardRequest(content):
            logger.info("[Tarot] 用户请求单张塔罗牌")  
            reply = Reply()  
            image = self.TarotSingleCard()  # 获取单张塔罗牌
            reply.type = ReplyType.IMAGE if image else ReplyType.TEXT  
            reply.content = image if image else "未找到卦图"  
            e_context['reply'] = reply  
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑  
        elif self.TarotThreeCardsRequest(content):
            logger.info("[Tarot] 用户请求三牌阵")
            reply = Reply()
            image = self.TarotThreeCards()  # 获取三牌阵
            reply.type = ReplyType.IMAGE if image else ReplyType.TEXT
            reply.content = image if image else "获取三牌阵失败"
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
        elif self.TarotCrossCardsRequest(content):
            logger.info("[Tarot] 用户请求十字牌阵")
            reply = Reply()
            image = self.TarotCrossCards()  # 获取十字牌阵
            reply.type = ReplyType.IMAGE if image else ReplyType.TEXT
            reply.content = image if image else "获取十字牌阵失败"
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
    def get_help_text(self, **kwargs):  
        """获取帮助文本"""  
        help_text = "请按照以下格式：\n[抽牌]：获取你的单张塔罗牌\n[三牌阵]：获取塔罗牌三牌阵\n[十字牌阵]：获取塔罗牌十字牌阵\n"  
        return help_text
