import datetime
import json
import os
import winsound
import time
from selenium.webdriver import ChromeOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 定义参数变量
options_api = {
    'detect_direction': 'true',
    'language_type': 'CHN_ENG',
}

options = ChromeOptions()
options.binary_location = r'C:\Users\demo\AppData\Local\Chromium\Application\Chromium.exe'
options.add_argument('--start-maximized')
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 禁用自动控制
options.add_experimental_option('useAutomationExtension', False)  # 禁用扩展
options.add_experimental_option("prefs",
                                {"credentials_enable_service": False,
                                 "profile.password_manager_enabled": False})  # 禁用密码保存
# 禁止弹窗
prefs = {
    'profile.default_content_setting_values':
        {
            'notifications': 2
        }
}
# 禁止弹窗加入
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(r'chromedriver.exe',
                          options=options)
driver.implicitly_wait(3)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                       {
                           "source": """
                            Object.defineProperty(navigator, 'webdriver', {
                              get: () => undefined
                            })
                          """
                       })


# options.add_argument('--proxy-server=1.2.3.4:5678')


def hightlight(element):
    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, "border: 2px solid red;")


def change_hightlight(element, j):
    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element,
                          f"border: {2 * j}px solid yellow;")


def cancel_hightlight(element):
    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, "border: 2px solid yellow;")


def start_or_stop(ch_bt):
    driver.execute_script("arguments[0].click();", ch_bt)  # js点击挑战答题
    # ch_bt.click()  # 点击挑战答题
    ch_cishu = get_cishu()  # 检查是否已答题
    time.sleep(0.3)
    if ch_cishu:
        hightlight(ch_cishu)
        print('今日已答题')
        name, score = get_score_name()
        change_acount_info(name, score)
        # driver.close()
        return False
    else:
        start_button = find_start_button()  # 检测 开始挑战按钮
        hightlight(start_button)  # 高亮 开始挑战

        music = driver.find_element_by_class_name('sound-effect')
        if '关闭' in music.text:
            hightlight(music)
            music.click()
            time.sleep(0.5)
        print('今日可以答题')
        driver.execute_script("arguments[0].click();", start_button)  # js点击开始挑战
        # start_button.click()     # 已用js取代
        return True


def get_cookies(username):
    dict_cookies = driver.get_cookies()  # 获取list的cookies
    json_cookies = json.dumps(dict_cookies)  # 转换成字符串保存

    with open(f'./cookies/{username}.txt', 'w') as f:
        f.write(json_cookies)


def load_cookies():
    """
    如果文件存在，就从本地读取cookies并刷新页面,成为已登录状态
    """
    old_url = 'https://aqy.lgb360.com/#/login'
    if os.path.exists(f'./cookies/{username}.txt'):
        with open(f'./cookies/{username}.txt', 'r', encoding='utf8') as f:
            list_cookies = json.loads(f.read())

        for cookie in list_cookies:
            cookie_dict = {
                'domain': '.aqy.lgb360.com',
                # 'domain': '.lgb360.com',
                'name': cookie.get('name'),
                'value': cookie.get('value'),
                "expires": '',
                'path': '/',
                'httpOnly': False,
                'HostOnly': False,
                'Secure': False
            }
            driver.add_cookie(cookie_dict)
        driver.refresh()
        time.sleep(0.5)
        current_url = driver.current_url
        # print(current_url)
        if current_url != old_url:  # 如果页面跳转
            print('cookies load finished')
            get_cookies(username)  # 存cookies
            login_info = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "challenge-info")))
            time.sleep(1)
            # print(repr(login_info.text))
            if '无' in login_info.text:
                print('cookies invalid')
                os.remove(f'./cookies/{username}.txt')
                driver.delete_all_cookies()
                driver.refresh()
                return login_and_check()
            else:
                return only_check()
        else:
            print('failed')
            driver.delete_all_cookies()
            driver.refresh()
            return login_and_check()
    else:
        print('no exists cookies')
        driver.refresh()
        return login_and_check()


def login_and_check():
    inputs = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.CLASS_NAME, "el-input__inner")))
    # inputs = driver.find_elements_by_class_name('el-input__inner')  # 三个输入框
    # login_button = driver.find_element_by_class_name("signIn.login-in")  # 登录按钮(空格写成.)
    # yzm_ele = driver.find_element_by_tag_name('img')  # 验证码图片
    inputs[0].send_keys(username)
    inputs[1].send_keys(password)
    # hightlight(inputs[2])
    inputs[2].click()
    winsound.Beep(3333, 600)

    n = driver.window_handles  # 获取当前页面所有的句柄
    driver.switch_to.window(n[0])  # 切换至最前面的页面

    ch_bt = get_ch_bt()  # 检查是否出现 挑战答题go
    get_cookies(username)  # 存cookies

    if ch_bt:
        hightlight(ch_bt)  # 高亮 挑战答题go
        finish_status = start_or_stop(ch_bt)  # 点击并判断是否需要答题
        return finish_status


def only_check():
    ch_bt = get_ch_bt()  # 检查是否出现 挑战答题go
    if ch_bt:
        hightlight(ch_bt)  # 高亮 挑战答题go
        finish_status = start_or_stop(ch_bt)  # 点击并判断是否答题
        return finish_status


def get_question():
    q_ele = driver.find_element_by_class_name('question-text')  # 题目
    a_ele = driver.find_element_by_class_name('question-answer')  # 选项

    while True:
        # time.sleep(1)
        try:
            # print('原题：', repr(q_ele.text))
            # print(repr(a_ele.text))
            # print('—————' * 20 + '----' + '—————' * 20)
            tk_q = q_ele.text.split('.')[1].strip()
            tk_a = a_ele.text.split('\n')
            # print(tk_q)
            # print(tk_a)
            # print('—————' * 20 + '----' + '—————' * 20)
            #  只存题目
            tk = {}
            tk['q'] = tk_q
            tk['a'] = tk_a
            # print('question:', tk)
            return tk
        except Exception as e:
            print('question no content:', e)
            pass


def get_ans(tk_q):
    with open(r'C:\Users\demo\PycharmProjects\pythonProject\cn\a_selenium_demo\all_all.txt', 'r',
              encoding='utf-8') as f:
        for row in list(f)[:]:
            res = eval(row)
            if tk_q.replace('（ ）', '()').replace(' ', '') == res['q'].replace(' ', ''):
                # if tk_q.replace('（ ）', '()') == res['q']:
                # print('answer：', res['ans'])
                return res['ans']  # 返回答案


def get_score_name():
    info = driver.find_element_by_class_name('challenge-info')
    for i in range(10):
        name = info.text.split('\n')[1]
        score = info.text.split('：')[1]
        if score != '0':
            return name, score
        else:
            time.sleep(1)


def save_topic():
    try:
        ans_ele = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "Correct")))
        # print('ans_ele.text:', repr(ans_ele.text))  # 内容
        tk_ans = ans_ele.text.split('\n')[1].split(':')[1]
        if tk_ans:
            pass
        else:
            tk_ans = ans_ele.text.split('\n')[2]
        tk_ans = tk_ans.split(',')
        tk_ans = ''.join(tk_ans)
        tk['ans'] = tk_ans
        print('tk:', tk)
        with open('topic.txt', 'a', encoding='utf-8') as f:
            f.write(str(tk))
            f.write('\n')
    except Exception as e:
        save_page('error_sucess')  # 保存网页
        print('获取网页答案', e)


def remove_duplicates():
    temp_list = []
    topic_list = []
    with open('topic.txt', 'r', encoding='utf-8') as f:
        for row in f:
            row = eval(row)
            if row['q'] not in temp_list:
                temp_list.append(row['q'])
                topic_list.append(row)
    topic_list.sort(key=lambda x: x['q'])
    with open('topic.txt', 'w', encoding='utf-8') as f:
        for i in topic_list:
            f.write(str(i))
            f.write('\n')


def click_ans(ans, tk):
    # 点击答案
    xuanxiang = driver.find_elements_by_class_name('foo-answer')  # 选项
    ans_dic = {'A': 0, 'B': 1, 'C': 2, 'D': 3, }
    ans_lst = []
    for i in ans:
        ans_lst.append(ans_dic[i])
    try:
        for j in ans_lst:  # 点击答案
            time.sleep(0.3)
            # driver.execute_script("arguments[0].click();", xuanxiang[j])   # js
            xuanxiang[j].click()
    except Exception as e:
        print('点击答案', e)
    time.sleep(1)

    # 如果有提交，点击提交
    if len(ans) > 1:
        try:
            sub_bt = driver.find_element_by_class_name('submission')  # 提交按钮
            # print('提交按钮是否可用：', sub_bt.is_enabled())
            hightlight(sub_bt)
            sub_bt.click()
        except Exception as e:
            print('提交按钮找不到：', e)
            winsound.Beep(3333, 600)
    save_page('tj')  # 保存网页

    # 保存内容
    save_topic()

    # 继续或完成挑战
    answer_info = get_all().text
    if '继续挑战' in answer_info:  # 如果'继续挑战'可见，高亮、并点击
        next_bt = get_next(driver)  # 获取‘继续挑战’按钮
        # hightlight(next_bt)
        # driver.execute_script("arguments[0].click();", next_bt)  # js
        next_bt.click()
    else:
        finish_bt = get_finish(driver)  # 获取‘挑战完成’按钮
        cancel_hightlight(finish_bt)
        finish_bt.click()
        time.sleep(1)
        try:
            reback = driver.find_element_by_class_name('back_btn')  # 挑战完成按钮
        except Exception as e:
            pass
        else:
            reback.click()
            name, score = get_score_name()
            change_acount_info(name, score)
            driver.delete_all_cookies()
            # print('del cookies:', driver.get_cookies())
            driver.refresh()
            driver.switch_to.alert.accept()
            return 1


def change_acount_info(name, score):
    file_data = ''
    with open('name.txt', "r", encoding="utf-8") as f:
        for row in f:
            row = eval(row)
            if row['username'] == username:
                row['state'] = '3'
                row['name'] = name
                row['score'] = score
                row['date'] = str(today_date)
            row = str(row)
            file_data += row + '\n'
    with open('name.txt', "w", encoding="utf-8") as f:
        f.write(file_data)


def save_page(filename):
    time0 = time.time()
    page = driver.page_source
    with open(f'../hello/{filename}{time0}.html', 'wb') as f:
        f.write(page.encode())


def get_next(driver):
    #   继续挑战
    try:
        return WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'继续挑战')]")))
    except Exception as e:
        return None


def get_all():
    #   继续挑战
    try:
        return WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "Correct")))
    except Exception as e:
        return None


def get_finish(driver):
    #   挑战完成
    try:
        return WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'挑战完成')]")))
    except Exception as e:
        return None


def get_ch_bt():
    #   挑战答题go
    try:
        return WebDriverWait(driver, 999).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "challenge-btn")))
    except Exception as e:
        pass


def find_start_button():
    #   开始答题按钮
    try:
        return WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "start-answering")))
    except Exception as e:
        return None


def get_cishu():
    #   次数
    try:
        driver.find_element_by_xpath("//*[contains(text(),'今日挑战次数已用')]")
        return driver.find_element_by_xpath("//*[contains(text(),'今日挑战次数已用')]")
    except Exception as e:
        return None


def get_account():
    with open('name.txt', "r", encoding="utf-8") as f:
        for row in f:
            row = eval(row)
            if row['date'] != str(today_date):
                # if row['state'] == '2' or row['date'] != str(today_date):
                # if row['state'] == '0':
                return row['username'], row['password']
        else:
            return None, None


if __name__ == '__main__':
    remove_duplicates()
    driver.get("https://aqy.lgb360.com/#/")
    for i in range(100):
        finish_flag = 0
        count = 1
        start_time = time.time()
        now = datetime.datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        username, password = get_account()  # 获取没答题的账号
        if username:
            driver.delete_all_cookies()
            finish_status = load_cookies()  # 加载cookies
            if finish_status:
                while True:
                    try:
                        print('—————' * 20 + f'—等待第{count}题加载—' + '—————' * 20)
                        time.sleep(2)
                        count += 1
                        tk = get_question()  # 获取题目
                        ans = get_ans(tk['q'])  # 获取答案
                        if ans:  # 如果有答案，点击答案
                            try:
                                finish_flag = click_ans(ans, tk)
                            except Exception as e:
                                print('点击答案', e)
                            else:
                                if finish_flag == 1:
                                    end_time = time.time()
                                    print('用时：', end_time - start_time)
                                    # print(finish_flag)
                                    break
                        else:  # 新题
                            try:
                                # 高亮标识,等待12s
                                explain = driver.find_element_by_class_name('explain')
                                winsound.Beep(1111, 3000)
                                for j in range(13)[::-1]:
                                    time.sleep(1)
                                    change_hightlight(explain, j)
                                # 高亮结束，定位'继续挑战'按钮，
                                next_bt = get_next(driver)  # 继续
                                if next_bt:  # 如果'继续挑战'可见，高亮、点击
                                    time.sleep(2)
                                    hightlight(next_bt)
                                    #111111
                                    save_page('noanswer')  # 保存网页
                                    # driver.execute_script("arguments[0].click();", next_bt)  # js
                                    next_bt.click()
                            except Exception as e:
                                save_page('last')  # 保存网页
                                print('点击提交', e)
                    except Exception as e:
                        print('搜题查找', e)
                        break
        else:
            print('已无可答账号')
            driver.close()
            break
