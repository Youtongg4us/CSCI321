from flask import Flask, request, render_template, redirect, url_for
import requests
import os

from Control.User.loginController import LoginController

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from flask import Flask, request, render_template, redirect, url_for,abort,jsonify,session
from werkzeug.exceptions import InternalServerError,BadRequest
#slow start when loadin ML functions, normal turn off
# from Control.User.requestForPrediction import RequestForPrediction
#

from Control.User.SignupController import *
from Control.IndividualUser.getAccountInfo import *
from Control.IndividualUser.updatePersonalInfo import *
from Control.User.changePasswordController import *
from Control.User.newsController import *
from Control.premiumUser.get_predictionData_by_symbol import *
from Control.User.commentController import *
from Control.premiumUser.recommendationListController import *
from Control.User.notificationController import *
from Control.premiumUser.get_followList_by_accountId import *
from Control.premiumUser.get_threshold_by_symbol_and_id import *
from Control.User.get_accounts_by_userName import *
from Control.User.get_account_by_accountId import *
from Control.premiumUser.remove_notification_by_id import *
from Control.premiumUser.remove_threshold_settings_by_thresholdId import *
from Control.User.insert_review_by_id import *
from Control.premiumUser.update_watchlist import *
from Control.premiumUser.get_watchlist_by_accountID import *
from Control.User.get_who_follows_me_by_accountID import *
from Control.premiumUser.update_threshold_settings import *
from Control.User.remove_follower_in_followList_by_id import *
from Control.User.insert_followList_by_id import *
from Control.premiumUser.update_follower_in_followList_by_id import *
from Control.User.addWatchListController import *
import hashlib
from flask import Flask, redirect
app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = 'csci314'

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
app = Flask(__name__)

@app.route('/add_watchlist', methods=['POST'])
def add_watchlist():
    try:
        data = request.json
        stockSymbol = data.get('symbol')
        #accountId = session.get('user')['accountId']
        # Hard Code for test
        accountId = 1
        print(f"Account ID: {accountId}, Stock Symbol: {stockSymbol}")

        if Watchlist().is_stock_in_watchlist(accountId, stockSymbol):
            return jsonify({'success': False, 'message': 'Already in Watchlist'})

        AddWatchListController().add_to_watchlist(accountId, stockSymbol)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/friend',methods=['GET','POST'])
def friend_list():
    if request.method == 'GET':
        followList = GetFollowListByAccountId().get_followList_by_accountId("1")
        who_follow_me_list = Get_who_follows_me_by_accountID().get_who_follows_me_by_accountID("1")
        account = GetAccountByAccountId().get_account_by_accountId("1")
        return render_template("/system/friend.html",followList=followList,who_follow_me_list=who_follow_me_list,account=account)
@app.route('/ratingComment', methods=['GET', 'POST'])
def ratingComment():
    if request.method == 'GET':
        return render_template("/system/RatingComment.html")
    if request.method == 'POST':
        data = request.json
        Insert_review_by_id().insert_review_by_id("1",data.get("rating"),data.get("comment"))
        return jsonify({'success': True})

@app.route('/insert_followList/<string:followedId>', methods=['GET', 'POST'])
def insert_followList(followedId):
    InsertFollowListById().insert_followList_by_id("1",followedId)
    return jsonify({'success': True})

@app.route('/remove_follower_in_followList/<string:followedId>', methods=['GET', 'POST'])
def remove_follower_in_followList(followedId):
    RemoveFollowerInFollowListById().remove_follower_in_followList_by_id("1",followedId)
    return jsonify({'success': True})
@app.route('/toggle-notification',methods=['GET','POST'])
def toggle_notification():
    data = request.json
    UpdateFollowerInFollowListById().update_follower_in_followList_by_id("1",data["followId"],data["notifyMe"])
    return jsonify({'success': True})
@app.route('/search/<string:content>')
def search(content):
    accountsList = GetAccountsByUserName().get_accounts_by_userName(content,"1")
    accountFavoList = GetFollowListByAccountId().get_followList_by_accountId_List("1")
    stockWatchList = GetWatchlistByAccountID().get_watchlist_by_accountID("1")
    return render_template("/system/search.html",content=content,accountsList=accountsList,stockWatchList=stockWatchList,accountFavoList=accountFavoList)
@app.route('/searchSymbol/')
@app.route('/mainPage', methods=['GET', 'POST'])
def mainPage():
    account = GetAccountByAccountId().get_account_by_accountId("1")
    return render_template('mainPage.html',account=account)

#remove notification
@app.route('/remove_notification', methods=['POST'])
def remove_notification():
    data = request.json
    notificationId = data.get('notificationId')
    notificationType = data.get('notificationType')
    referenceId = data.get('referenceId')

    if notificationType == "threshold":
        Remove_notification_by_id().remove_notification_by_id(notificationId)
        Remove_threshold_settings_by_thresholdId().remove_threshold_settings_by_thresholdId(referenceId)
    else:
        Remove_notification_by_id().remove_notification_by_id(notificationId)

    return jsonify({'success': True})

# user login main page
@app.route('/recommendation_news/<int:page>', methods=['GET', 'POST'])
def recommendation_news(page):
    # hard code for test, countries and industries store in session['preferences']
    countries = 'us'
    industries = 'Technology'
    result = NewsController().get_recommendation_news(countries,industries,str(page))
    return jsonify(result)
# user login main page
@app.route('/recommendation_symbol', methods=['GET', 'POST'])
def recommendation_symbol():
    # hard code for test, userId in session['user']
    accountId = 1
    return jsonify(RecommendationListController().get_recommendationList_by_accountId(accountId))
@app.route('/get_notification',methods=['GET', 'POST'])
def get_notification():
    # hard code for test, userId in session['user']
    accountId = 1
    return jsonify(NotificationController().get_notifications_by_accountId(accountId))


@app.route('/symbol_news/<string:symbol>/<int:page>', methods=['GET', 'POST'])
def symbol_news(symbol,page):
    return jsonify(NewsController().get_news_by_symbol(symbol,str(page)))

@app.route("/searchSymbol/<string:symbol>", methods=['GET', 'POST'])
def searchSymbol(symbol):
    if request.method == 'POST':
        return jsonify(StockDataController().search_stock(symbol))

@app.route('/symbol/<string:symbol>')
def symbol(symbol):
    user = GetAccountByAccountId().get_account_by_accountId("1")
    stockData = StockDataController().get_update_stock_data(symbol,"1mo")
    stockInfo = StockDataController().get_stock_info_full(symbol)
    predictionresult = GetPredictionDataBySymbol().get_predictionData_by_symbol(symbol)
    threshold = Get_threshold_by_symbol_and_id().get_threshold_by_symbol_and_id("1",symbol)
    watchList = GetWatchlistByAccountID().get_watchlist_by_accountID("1")
    return render_template('/PremiumUser/symbolPage.html', stockData=stockData,stockInfo=stockInfo,predictionresult=predictionresult,threshold=threshold,watchList=watchList,user=user)
@app.route('/request_for_prediction/<string:symbol>/<string:days>/<string:model>',methods=['POST'])
def request_for_prediction(symbol,days,model):
    # pass in (symbol,days,accountId) to backend, use 'model' to determine which model to use
    #  symbol and accountId only use to create notification
    print(symbol,days,model)
    return jsonify({'success': True})

@app.route('/submit_comment',methods=["POST"])
def submit_comment():
    data = request.json
    CommentController().insert_comment("1",data["symbol"],data["comment"])
    return jsonify({'success': True})
@app.route('/update_watchList',methods=['POST'])
def update_watchList():
    data = request.json
    UpdateWatchlist().update_Watchlist("1",data.get("watchList"))
    return jsonify({'success': True})

@app.route("/update_threshold_setting/<string:symbol>/<string:threshold>", methods=['POST'])
def update_threshold_setting(symbol, threshold):
    Update_threshold_settings().update_threshold_settings("1", symbol, float(threshold))
    return jsonify({'success': True})
@app.route('/symbol_comments/<string:symbol>')
def symbol_comments(symbol):
    return jsonify(CommentController().get_comments_by_symbol(symbol))

@app.route('/emailVerification', methods=['GET', 'POST'])
def emailVerification():
    return render_template("/system/emailVerification.html")

@app.route('/preferenceSetup', methods=['GET', 'POST'])
def preferenceSetup():
    return render_template("/system/preferenceSetUp.html")
@app.route('/demo')
def demo():
    list = StockDataController().get_recommendation_stock_by_preference("us", "Energy,Technology")
    recommendationList = []
    for stock in list:
        try:
            recommendationList.append(StockDataController().get_stock_info_medium(stock))
        except Exception as e:
            continue

    return render_template('demo.html',recommendationList = recommendationList)
@app.route('/stock_info_minimum/<string:symbol>', methods=['GET'])
def stock_info_minimum(symbol):
    return jsonify(StockDataController().get_stock_info_minimum(symbol))

@app.route('/update_stock_data/<string:symbol>/<string:period>', methods=['GET'])
def update_stock_data(symbol, period):
    return jsonify(StockDataController().get_update_stock_data(symbol, period))

@app.route('/stock_data_medium/<string:symbol>',methods=['GET'])
def stock_data_medium(symbol):
    return jsonify(StockDataController().get_stock_info_medium(symbol))

@app.route('/stock_info_full/<string:symbol>', methods=['GET'])
def stock_info_full(symbol):
    return jsonify(StockDataController().get_stock_info_full(symbol))
@app.route('/api',methods=['GET'])
def api():
    try:
        apikey = request.args.get('apikey')
        symbol = request.args.get('symbol')
        timeframe = request.args.get('timeframe')
        model = request.args.get('model')
        layers = request.args.get('layers')
        neurons = request.args.get('neurons')

        return
    except Exception as e:
        return jsonify({"error":str(e)})


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template("system/login.html")
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        session['user'] = LoginController().login(username, password)
        return jsonify({'success':True})
    except Exception as e:
        return jsonify({'success':False,'error':str(e)})

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == 'GET':
        return render_template("system/signup.html")
    try:
        data = request.json
        SignupController().individualSignUp(data['profile'],data['username'],data['email'],data['password'],data['repassword'],data['invitationCode'])
        return jsonify({'success':True})
    except Exception as e:
        return jsonify({'success':False,'error':str(e)})
@app.route('/businessSignup',methods=['POST','GET'])
def businesssignup():
    if request.method == 'GET':
        return render_template("system/businessSignup.html")
    try:
        data = request.json
        pass
    except Exception as e:
        return jsonify({'success':False,'error':str(e)})

@app.route('/accountInfo',methods=['POST','GET'])
def accountInfo():
    if request.method == 'GET':
        #todo hard code for test
        #session['user']  = {'accountId': 1, 'userName': 'lixiang', 'apikey': 'abcdefg', 'hashedPassword': 'e10adc3949ba59abbe56e057f20f883e', 'email': 'lixiang@gmail.com', 'bio': 'Welcome to stock4me!', 'profile': 'free', 'status': 'valid', 'apikeyUsageCount': 0,'accountType':'individual' 'createDateTime': datetime.datetime(2024, 6, 14, 18, 8, 2)}
        session['user'] = GetAccountInfo().getAccountInfo("1")
        if session['user']['accountType'] == 'individual':
            if session['user']['profile'] == 'free':
                return render_template("individualFreeUser/accountInfo.html",user = session['user'])
            elif session['user']['profile'] == 'premium':
                pass
        elif session['user']['accountType'] == 'business':
            pass

#handle personal info. update(name,bio,email), business update(name,bio,email,companyName)
@app.route('/updatePersonalInfo', methods=['POST'])
def updatePersonalInfo_FreeUser():
    # if 'user' not in session:
    #     print("user not in session")
    #     return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    accountType = request.json.get('accountType')
    accountId = request.json.get('accountId')
    bio = request.json.get('bio')
    userName = request.json.get('userName')
    email = request.json.get('email')
    if accountType == 'individual':
        success = UpdatePersonalInfo().updatePersonalInfo(accountId,userName,email,bio)
    elif accountType == 'business':
        #company, updateBusinessInfo()
        pass

    if success:
        session['user']['bio'] = bio
        session['user']['userName'] = userName
        session['user']['email'] = email
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to update bio in the database'}), 500

@app.route('/changePassword', methods=['POST'])
def change_password():
    # if 'user' not in session:
    #     return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        old_password = request.json.get('oldPassword')
        new_password = request.json.get('newPassword')
        userName = session['user']['userName']
        if hashlib.md5(old_password.encode()).hexdigest() != session['user']['hashedPassword']:
            raise Exception('Invalid old password')
        if session['user']['accountType'] == 'individual':
            session['user']['hashedPassword'] = ChangePasswordController().changeIndividualPassword(userName,old_password,new_password)
        elif session['user']['accountType'] == 'business':
            pass
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False,'error':str(e)})



@app.route('/predictionResult',methods=['POST','GET'])
def predictionresult():
    if request.method == 'GET':
        #hard code for test
        #session['user']  = {'accountId': 1, 'userName': 'lixiang', 'apikey': 'abcdefg', 'hashedPassword': 'e10adc3949ba59abbe56e057f20f883e', 'email': 'lixiang@gmail.com', 'bio': 'Welcome to stock4me!', 'profile': 'free', 'status': 'valid', 'apikeyUsageCount': 0,'accountType':'individual' 'createDateTime': datetime.datetime(2024, 6, 14, 18, 8, 2)}
        # session['user'] = GetAccountInfo().getAccountInfo("1")
        # predictionResult = GetRequestRecord().getRequestRecord(session['user']['apikey'])
        # print(predictionResult)
        if session['user']['accountType'] == 'individual':
            if session['user']['profile'] == 'free':
                return render_template("individualFreeUser/predictionResult.html")
            elif session['user']['profile'] == 'premium':
                pass
        elif session['user']['accountType'] == 'business':
            pass

@app.route('/updatePredictionResult',methods=['GET'])
def updatePredictionResult():
    # session['user'] = GetAccountInfo().getAccountInfo("1")
    return

@app.route('/deletePrediction/<int:requestId>', methods=['DELETE'])
def deletePrediction(requestId):

    return jsonify({'success':True})
@app.route('/verifyInput',methods=['POST'])
def verifyInput():
    if request.method == 'POST':
        try:
            apikey = session['user']['apikey']
            tickerSymbol = request.json.get('tickerSymbol')
            timeRange = request.json.get('timeRange')
            model = request.json.get('model')
            layers = request.json.get('layers')
            neurons = request.json.get('neurons')

            return jsonify({'success':True})
        except Exception as e:
            return jsonify({'success':False,'error':str(e)})
@app.route('/predict', methods=['GET','POST'])
def predict():
    if request.method == 'GET':
        #todo hard code for test
        # session['user'] = GetAccountInfo().getAccountInfo("1")
        return render_template("individualFreeUser/RequestPrediction.html")
    if request.method == 'POST':
        try:
            apikey = session['user']['apikey']
            tickerSymbol = request.json.get('tickerSymbol')
            timeRange = request.json.get('timeRange')
            model = request.json.get('model')
            layers = request.json.get('layers')
            neurons = request.json.get('neurons')

            return jsonify({'success':True})
        except Exception as e:
            return jsonify({'success':False,'error':str(e)})
    # print(apikey,tickerSymbol,timeRange,model,layers,neurons)
    # print(type(apikey),type(tickerSymbol),type(timeRange),type(model),type(layers),type(neurons))
    #
@app.route('/',methods=['GET'])
def officialWeb():
    return render_template("system/template.html")

@app.route('/history',methods=['GET'])
def history():
    return render_template("system/history.html")

@app.route('/redirectToUserPage',methods=['GET'])
def redirectToUserPage():
    if 'user' in session:
        if session['user']["accountType"] == 'individual':
            if session['user']["profile"] == "free":
                return redirect(url_for('accountInfo'))
    else:
        return redirect(url_for('login'))

@app.route('/logout',methods=['GET'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/documentation',methods=['GET'])
def documentation():
    return render_template("system/documentation.html")

@app.route('/contact',methods=['GET'])
def contact():
    return redirect("https://csit321fyp24s2g27.wixsite.com/group27")

# Dynamically checking that user-selected stocks have not exceeded thresholds
# Define a cache to store recent notifications
notification_cache = {}

# def threshold_notification():
#     global notification_cache
#     premiumUserList = GetPremiumUsersController().getPremiumUsers()
#     for user in premiumUserList:
#         thresholds = GetThresholdSettingById().get_threshold_settings_by_id(user)
#         if thresholds:
#             for threshold in thresholds:
#                 symbol = StockDataController().get_stock_info_minimum(threshold["stockSymbol"])
#                 if abs(symbol["relative_change"]) > threshold['changePercentage']:
#                     cache_key = (user, threshold["stockSymbol"])
#                     current_time = time.time()
#                     # Checking for recent notifications
#                     if cache_key not in notification_cache or (current_time - notification_cache[cache_key] > 3600):  # one hour
#                         notificationWord = f"Hi, Your followed {threshold['stockSymbol']} that exceeds your threshold."
#                         NotificationController().set_notification(user, notificationWord, "threshold", threshold['thresholdId'],threshold['stockSymbol'])
#                         notification_cache[cache_key] = current_time
#                         Personal_who_follow_user_List = GetAccountListByFollowedId().get_accountList_by_followedId(user)
#                         if Personal_who_follow_user_List:
#                             for userFollow in Personal_who_follow_user_List:
#                                 if userFollow['notifyMe'] == 1:
#                                     notificationWord = f"There have been updates to stock {threshold['stockSymbol']} for user {userFollow['userName']} you follow! Please check"
#                                     hashed_symbol = int(hashlib.md5(threshold['stockSymbol'].encode()).hexdigest(),16)%(2**31-1)
#                                     NotificationController().set_notification(userFollow['followListAccountId'],notificationWord,"friend_threshold",hashed_symbol,threshold['stockSymbol'])

# def run_schedule():
#     schedule.every(2).seconds.do(threshold_notification)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

if __name__ == '__main__':
    # schedule_thread = threading.Thread(target=run_schedule)
    # schedule_thread.daemon = True
    # schedule_thread.start()
    app.run(host='0.0.0.0',port=80,debug=True)
