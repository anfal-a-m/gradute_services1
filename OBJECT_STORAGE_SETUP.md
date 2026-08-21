# إعداد التخزين الدائم لملفات البوابة

تستخدم البوابة تخزينًا خاصًا متوافقًا مع S3 لملفات السير الذاتية والشهادات
والتقارير. تبقى ملفات التصميم تحت `static` ويقدمها WhiteNoise بصورة مستقلة.

## Cloudflare R2

1. من Cloudflare افتح **Storage & databases → R2 → Overview**.
2. أنشئ حاوية خاصة باسم مثل `graduate-services-media`.
3. من **Manage R2 API Tokens** أنشئ رمزًا بصلاحية **Object Read & Write**
   ومقيدًا بهذه الحاوية فقط.
4. احتفظ بـ Access Key ID وSecret Access Key وS3 API endpoint.
5. في Render افتح خدمة `gradute-services1` ثم **Environment** وأضف:

| المتغير | القيمة |
|---|---|
| `MEDIA_BUCKET_NAME` | اسم حاوية R2 |
| `MEDIA_ACCESS_KEY_ID` | Access Key ID |
| `MEDIA_SECRET_ACCESS_KEY` | Secret Access Key |
| `MEDIA_S3_ENDPOINT_URL` | `https://ACCOUNT_ID.r2.cloudflarestorage.com` |
| `MEDIA_S3_REGION` | `auto` |
| `MEDIA_SIGNED_URL_EXPIRE` | `900` |

6. اختر **Save, rebuild, and deploy**.

لا تجعل الحاوية Public. يولد Django روابط موقعة مؤقتة لمدة 15 دقيقة، ولا
تُحفظ المفاتيح في GitHub. إذا أضيف `MEDIA_BUCKET_NAME` دون بقية المفاتيح
سيتوقف التشغيل برسالة واضحة بدل حفظ الملفات خطأً على القرص المؤقت.

في البيئة المحلية، وعند غياب `MEDIA_BUCKET_NAME`، تستمر الملفات في مجلد
`media` بصورة طبيعية.
