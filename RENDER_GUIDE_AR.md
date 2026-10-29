# تشغيل بوت دليل الجامعات العراقي على Render (الخطة المجانية)

## مهم قبل البدء
- النسخة تحتوي على بحث حسب المعدل والحدود الأقرب + دليل الاختصاصات + الأقساط + الإدارة.
- تعمل عبر **Web Service** مبني باستخدام Dockerfile، **وليس Static Site**.
- يستخدم البوت **Telegram webhook**. يسجّل Webhook + Menu Button + Bot Commands تلقائياً عند تشغيل السيرفر؛ لا تحتاج تنفيذ أوامر على Render.
- Render Free تنام بعد **15 دقيقة بلا طلبات واردة**، والعودة قد تستغرق نحو دقيقة. طلب Telegram الوارد يساعد على إيقاظها، لكن قد تتأخر الاستجابة.
- تحذير حرج: **قاعدة البيانات الحالية SQLite على قرص الخدمة مؤقتة**. عند النوم أو restart أو redeploy، تضيع الملفات التي كتبها المستخدم، مثل معدلات الطلاب والمفضلات والتعديلات والتنبيهات والمراجعات. بيانات القبول والأقساط المضمّنة مع ملفات المشروع لا تضيع. **استعملها لاختبار خاص فقط، ولا تدعو الطلاب أو تحفظ بيانات مهمة قبل ربط قاعدة بيانات دائمة.**
- قاعدة Render Postgres المجانية تنتهي بعد 30 يوماً، ولا يصلح نقل SQLite إليها دون تحويل طبقة التخزين في الكود.

## 1) رفع الملفات إلى GitHub
1. فك `iraqi_university_guide_v4_render.zip` عندك.
2. ادخل مجلد `university-guide`، وارفع **محتوياته** إلى مستودع GitHub خاص. يجب أن يظهر `Dockerfile` و`app.py` و`render.yaml` في **جذر** المستودع، وليس داخل مجلد إضافي.
3. لا ترفع `.env` أو توكن البوت أو أي كلمة مرور. تجاهل مجلد `runtime/`.

## 2) إنشاء خدمة Render
1. افتح https://dashboard.render.com/ واضغط `New` ثم `Web Service`.
2. اختر GitHub واربط مستودعك، ثم `Connect`.
3. اكتب الاسم مثلاً `iraqi-university-guide`، واختر الفرع `main`.
4. اختر `Language/Runtime: Docker` (Render سيقرأ `Dockerfile`).
5. اختر الخطة `Free` ثم `Create/Deploy Web Service`.
6. لا تضع أوامر Build أو Start يدوية عند اختيار Docker، لأن `Dockerfile` موجود ويتكفل بها.
7. بعد نجاح النشر يعرض Render رابطاً على شكل `https://...onrender.com`. زر الرابط واختبر `/health`، يجب أن تظهر `status: ok`.

يمكنك استخدام `New > Blueprint` مع ملف `render.yaml` كبديل عن Web Service، **لا تنشئ الاثنين** حتى لا تحصل على خدمتين للبوت نفسه.

## 3) إضافة Environment Variables (أهم خطوة)
من داخل الخدمة: `Environment` > `Add Environment Variable`. اضبط القيم:

| Key | Value |
| --- | --- |
| `PREVIEW_MODE` | `false` |
| `REQUIRED_CHANNEL` | `@iwillsleep` |
| `DATA_DIR` | `/data` (مؤقت على الخطة المجانية) |
| `BOT_TOKEN` | توكن حقيقي جديد من `@BotFather`، ضعه في Render فقط |
| `ADMIN_PASSWORD` | كلمة مرور فريدة خاصة بك، 16 محرفاً أو أكثر |
| `WEBHOOK_SECRET` | سلسلة عشوائية 32 محرفاً أو أكثر؛ استخدم حروف إنكليزية وأرقام و`_` و`-` فقط |

`PUBLIC_URL` **اختياري على Render**: التطبيق يقرأ تلقائياً `RENDER_EXTERNAL_URL` من Render. لو عندك نطاق مخصص مختلف عن `onrender.com` ضعه كاملاً في `PUBLIC_URL` دون `/` بالنهاية.

لتوليد `WEBHOOK_SECRET` على أي كمبيوتر عندك عليه Python:

```sh
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

انسخ الناتج لحقل `WEBHOOK_SECRET` في Render، **لا تنشره في GitHub ولا ترسله لأي شخص**. إذا كتبت قيمة يدوية تجنب الرموز `+` و`/` و`=` والمسافات.

بعد الحفظ اختَر `Save, deploy` أو `Save, rebuild, deploy`. Render سيشغّل البوت ويربط Telegram تلقائياً؛ راقب `Logs` لأي رسالة `Telegram setup failed`.

## 4) تهيئة Telegram
1. افتح `@BotFather` وسوِّ بوت إذا ما عندك. انسخ التوكن وضعه في Environment بRender.
2. أضف **البوت أدمن بقناة `@iwillsleep`** حتى يستطيع التحقق من اشتراك الطلاب.
3. بعد النشر شغّل البوت من Telegram باستخدام `/start`. لو أنت مشترك تظهر لك واجهة الدليل. إذا ما مشترك يعطيك زر الاشتراك.
4. ابعث رقم معدل مثل `85.50`، وبعدها افتح الواجهة وأكمل الفرع والجنس. تأكد من ترتيب الأقرب المؤهّل ثم الأعلى بقليل.
5. راجع لوحة الإدارة عند `https://SERVICE.onrender.com/admin` بنفس `ADMIN_PASSWORD`.

## 5) إذا ما اشتغل
- إذا Render يعرض `Deploy failed` أو `No open ports detected`: اختر Docker وتأكد أن `Dockerfile` في جذر GitHub وأن Dockerfile موجود في أحدث Commit. السيرفر يربط `0.0.0.0` على `$PORT`.
- إذا الرابط يفتح والبوت لا يستجيب: افتح `Logs` وابحث عن رسالة `Telegram setup failed`؛ راجع `BOT_TOKEN` وصحة سر الـWebhook، وأضف البوت أدمن للقناة.
- إذا يظهر `Set ... WEBHOOK_SECRET ...`: السر يجب 32 محرفاً على الأقل، و`ADMIN_PASSWORD` لا تقل عن 16 محرفاً.
- إذا يظهر `PREVIEW_MODE must never...`: غيّر PREVIEW_MODE إلى false واحفظ المتغيرات.
- إذا `/health` يعمل لكن Telegram Mini App يظهر خطأ تسجيل دخول: افتح الواجهة **من زر البوت داخل Telegram**؛ فتح رابط الويب بشكل مستقل لا يزوده بيانات دخول Telegram.
- إذا رجعت المفضلات والمعدلات فارغة بعد استيقاظ Render: هذا متوقّع مع SQLite المحلية في الخطة المجانية وليس خطأ بالفلتر.
- إذا بوت سابق شغال بنفس التوكن على Railway أو استضافة أخرى، أوقف الخدمة القديمة حتى لا تتضارب Webhooks.

## حماية الطلاب والإطلاق العام
لا تستخدم النسخة الحالية مع طلاب حقيقيين حتى تحوّل `storage.py` إلى PostgreSQL أو قاعدة خارجية دائمة بتوصيل آمن وتختبر النسخ الاحتياطي، وتراجع جودة بيانات القبول والإدارة. **مجرد إنشاء قاعدة PostgreSQL لا ينقل بيانات SQLite تلقائياً**. لا تضف قيمة وهمية لـ`PERSISTENT_STORAGE_READY` لإخفاء تحذير عدم ديمومة البيانات.
