# 📱 EduManage ERP - Android APK बनाने और ऐप चलाने की संपूर्ण गाइड

इस गाइड में **Android APK (`.apk`)** बनाने और ऐप को अपने फोन पर टेस्ट करने के सबसे आसान और 100% फ्री तरीके दिए गए हैं।

---

## 🌟 2 सबसे आसान तरीके APK बनाने के:

---

### 🥇 तरीका 1: **GitHub से 1-क्लिक में फ्री में APK डाउनलोड करें (बिना कोई सॉफ्टवेयर इंस्टॉल किए)** ⭐ *(सबसे आसान)*

अगर आपके कंप्यूटर में Flutter या Android Studio इंस्टॉल नहीं है, तो भी आप **GitHub Actions** के ज़रिए क्लाउड में सीधे APK बना सकते हैं:

1. अपने GitHub रिपॉजिटरी पेज पर जाएं: **[https://github.com/Abhi2701singh/school-erp](https://github.com/Abhi2701singh/school-erp)**
2. ऊपर मेन्यू में **`Actions`** टैब पर क्लिक करें।
3. बाईं तरफ **`Build Android APK`** वर्कफ़्लो चुनें।
4. दाईं तरफ **`Run workflow`** बटन पर क्लिक करें।
5. 2 से 3 मिनट में GitHub क्लाउड आपके लिए फ्रेश APK बनाकर तैयार कर देगा।
6. वर्कफ़्लो पूरा होने पर उस पर क्लिक करें और नीचे **`Artifacts`** सेक्शन से **`edumanage-school-erp-release-apk`** डाउनलोड कर लें! 🎉

---

### 🥈 तरीका 2: **अपने कंप्यूटर/लैपटॉप से 1-क्लिक में APK बनाएं (Local Build)**

अगर आपके कंप्यूटर में **Flutter SDK** इंस्टॉल है:

#### **macOS / Linux पर:**
```bash
# 1. mobile_app फोल्डर में जाएं
cd mobile_app

# 2. ऑटोमेटेड बिल्ड स्क्रिप्ट चलाएं
./build_apk.sh
```

#### **Windows पर:**
1. `mobile_app` फोल्डर में जाएं।
2. **`build_apk.bat`** फाइल पर डबल-क्लिक करें, या कमांड प्रॉम्प्ट (CMD) में चलाएं:
```cmd
cd mobile_app
build_apk.bat
```

#### **मैनुअल कमांड (कस्टम बिल्ड):**
```bash
cd mobile_app
flutter pub get
flutter build apk --release
```

📁 **तैयार APK फाइल कहाँ मिलेगी?**
`mobile_app/build/app/outputs/flutter-apk/app-release.apk`

---

## 📲 APK को Android फोन में कैसे इंस्टॉल करें:

1. तैयार हुई **`app-release.apk`** फाइल को अपने फोन में भेजें (USB केबल, WhatsApp या Google Drive के ज़रिए)।
2. फोन में फाइल मैनेजर खोलकर APK पर टैप करें।
3. अगर फोन **"Install from unknown sources"** पूछे, तो **Allow (अनुमति दें)** पर टिक करें।
4. **"Install"** पर क्लिक करें।
5. ऐप इंस्टॉल हो जाएगा और आपके फोन के होम स्क्रीन पर **EduManage ERP** का आइकॉन दिखेगा! 🚀

---

## 💻 ऐप को लाइव डेवलप / टेस्ट करने का तरीका (`flutter run`):

1. अपने फोन को USB केबल से कंप्यूटर से कनेक्ट करें (USB Debugging चालू रखें) या Android Emulator खोलें।
2. टर्मिनल में निम्नलिखित कमांड चलाएं:
```bash
cd mobile_app
flutter pub get
flutter run
```
3. ऐप लाइव आपके फोन पर खुल जाएगा और आप जो भी कोड बदलेंगे वह **Hot Reload (`r`)** से तुरंत फोन में दिखेगा!

---

## ⚙️ बैकएंड API सेटिंग्स:

यदि आप लोकल कंप्यूटर पर बैकएंड चला रहे हैं, तो `lib/core/constants/api_constants.dart` में अपना URL चेक कर सकते हैं:
- **लाइव रेंडर प्रोडक्शन**: `https://edumanage-school-erp.onrender.com/api/v1` (पहले से सेट है)
- **लोकल Android Emulator**: `http://10.0.2.2:8000/api/v1`
- **लोकल वाई-फाई डिवाइस**: `http://<YOUR_PC_IP>:8000/api/v1`
