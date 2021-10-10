# line-bot-project
Line生活小助手聊天機器人，功能包括:「查詢附近美食」、「發票兌獎」、「查詢天氣」、「查詢電影」。
# 開始使用
掃描QR code加好友

<img src="https://upload.cc/i1/2021/09/25/GXUnsd.png" alt="Cover" width="20%"/>

# 使用範例
### 初始畫面  
<img src="https://upload.cc/i1/2021/09/25/WGob2J.jpg" alt="Cover" width="30%"/>

### 查詢附近的美食
點選圖文選單中的「附近美食」，回傳操作說明。  
<img src="https://upload.cc/i1/2021/09/25/5hbk1G.jpg" alt="Cover" width="30%"/>

輸入地區地址或Line位置資訊後，聊天機器人會使用Google Maps API獲取經緯度，  
根據經緯度到「愛食記」網站爬取附近評價最好的十間餐廳並回傳。  
<img src="https://upload.cc/i1/2021/09/25/Qm3cjr.png" alt="Cover" width="30%"/>  

### 發票兌獎  
點選圖文選單中的「發票兌獎」，即可查詢本期和前期的中獎號碼。  
<img src="https://upload.cc/i1/2021/09/25/bE3ZJR.jpg" alt="Cover" width="30%"/>  

選取「輸入後三碼」，即可開始輸入發票最後三碼。  
<img src="https://upload.cc/i1/2021/09/25/1goO26.jpg" alt="Cover" width="30%"/>  

沒中獎的畫面。  
<img src="https://upload.cc/i1/2021/09/25/mKsYz1.jpg" alt="Cover" width="30%"/>  

### 查詢天氣  
點選圖文選單中的「查詢天氣」，回傳操作說明。  
利用LUIS來判斷使用者意圖，如果意圖為查詢天氣即會回傳目標的天氣狀況。  
<img src="https://upload.cc/i1/2021/09/25/5I0ZJf.jpg" alt="Cover" width="30%"/>  

### 查詢本周新片+場次  
點選圖文選單中的「本周新片」，回傳本週新上映的電影。  
<img src="https://upload.cc/i1/2021/09/25/ndsp6N.jpg" alt="Cover" width="30%"/>  

利用LUIS來判斷使用者意圖，如果意圖為查詢電影即會回傳該電影的場次資訊。  
<img src="https://upload.cc/i1/2021/09/25/CTUtqV.jpg" alt="Cover" width="30%"/>  

如果使用者的輸入有錯字或不在本周新片中則會請對方重新輸入。   
<img src="https://upload.cc/i1/2021/09/25/3sEQde.jpg" alt="Cover" width="30%"/>  

