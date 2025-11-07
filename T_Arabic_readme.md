# <div dir="rtl">🇸🇦 T-Arabic — عكس النص العربي بسهولة</div>
# <div dir="ltr">🇬🇧 T-Arabic — Arabic Text Reverser</div>

![Windows](https://img.shields.io/badge/Platform-Windows-blue) ![Python](https://img.shields.io/badge/Python-Bundled-orange) ![Version](https://img.shields.io/badge/Version-1.0.0-green)

---

## <div dir="rtl">🇸🇦 النسخة العربية</div>
<div dir="rtl">
**T-Arabic** هو تطبيق صغير وبسيط لعرض النصوص العربية بشكل صحيح في الألعاب أو البرامج التي لا تدعم العربية.  
يقوم التطبيق بعكس النصوص العربية وربط الحروف بشكل صحيح ثم ينسخها تلقائيًا إلى الحافظة.

### 🪶 المميزات

- 🔄 يعكس النص العربي تلقائيًا مع الحفاظ على الاتصال الصحيح للحروف  
- 📋 ينسخ النص المعدل تلقائيًا للحافظة  
- 🖱️ زر لتفعيل وضع Click-Through لتجاهل النقرات  
- 💾 حفظ آخر موقع للتطبيق عند الإغلاق  
- 🧱 واجهة بسيطة، صغيرة وشفافة  
- 🚫 لا يظهر في قائمة Alt+Tab  

### ⚙️ طريقة الاستخدام

1. شغّل `T-Arabic.exe`  
2. اكتب النص العربي في المربع — سيظهر طبيعيًا أثناء الكتابة  
3. سيُعكس النص تلقائيًا ويُنسخ للحافظة  
4. الصقه في اللعبة أو البرنامج (Ctrl + V)  
5. اضغط `-` لتفعيل وضع Click-Through  
6. اضغط `Delete` لمسح النص بالكامل بسرعة  

### 🧠 الاختصارات

| المفتاح | الوظيفة |
|--------|---------|
| `-`    | تفعيل/تعطيل وضع Click-Through |
| `Delete` | مسح النص بالكامل |

### 🧑‍💻 للمطورين
> ⚠️ مهم: يجب تثبيت Python قبل البدء

#### 🧱 إنشاء T-Arabic.exe
```bat
build_exe.bat
```

#### 📦 إنشاء ملف التثبيت
```bat
build_setup.bat
```
> ملاحظة: يجب تنفيذ `build_exe.bat` أولًا.

### 🛠 مشاكل معروفة
- بعض المشاكل مع الحروف: `ر`, `ز` عند العكس أو الربط

### 📁 هيكل المشروع
```
T-Arabic/
├── reverse_text_app.py
├── build_exe.bat
├── build_setup.bat
├── reverse_melon.ico
├── t_arabic_version.txt
├── position.json
└── README.md
```

### 💡 ملاحظات

- يعمل فقط على Windows  
- لا يحتاج مكتبات خارجية  
</div>

---

## <div dir="ltr">🇬🇧 English Version</div>
<div dir="ltr">
**T-Arabic** is a lightweight app for displaying Arabic text correctly in games or apps that don’t support RTL text.  
It automatically reverses and reshapes Arabic text, then copies it to the clipboard.

### 🪶 Features

- 🔄 Auto reshapes and reverses Arabic text  
- 📋 Auto copies text to clipboard  
- 🖱️ Click-Through toggle to ignore mouse clicks  
- 💾 Saves last window position  
- 🧱 Clean, minimal, transparent UI  
- 🚫 Hidden from Alt+Tab  

### ⚙️ How to Use

1. Run `T-Arabic.exe`  
2. Type Arabic text — it appears normal while typing  
3. Text is automatically reversed & copied to clipboard  
4. Paste it into your game or app (Ctrl + V)  
5. Press `-` to enable Click-Through  
6. Press `Delete` to clear all text instantly  

### 🧠 Shortcuts

| Key       | Action                     |
|-----------|----------------------------|
| `-`       | Toggle Click-Through mode  |
| `Delete`  | Clear all text instantly   |

### 🧑‍💻 Developer Guide
> ⚠️ Important: Python must be installed before building

#### 🧱 Build T-Arabic.exe
```bat
build_exe.bat
```

#### 📦 Build Setup Installer
```bat
build_setup.bat
```
> Note: `build_exe.bat` must be run first.

### 🛠 Known Issues
- Some issues with letters: `ر`, `ز` during reversing or shaping

### 📁 Project Structure
```
T-Arabic/
├── reverse_text_app.py
├── build_exe.bat
├── build_setup.bat
├── reverse_melon.ico
├── t_arabic_version.txt
├── position.json
└── README.md
```

### 💡 Notes

- Windows only  
- No external dependencies required
</div>
