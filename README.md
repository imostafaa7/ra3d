# ra3d 
ra3d https://target.com                  # افتراضي: 50 خيط GET
ra3d https://target.com -t 200            # 200 خيط
ra3d https://target.com -m GET POST -n 5000  # 5000 طلب
ra3d https://target.com --time 60          # لمدة 60 ثانية
ra3d https://target.com --random-url       # URLs عشوائية
ra3d https://target.com --body 'user=admin&pass={rand}' --cookie 'session=abc'
ra3d https://target.com -d 100             # تأخير 100ms بين الطلبات
ra3d https://target.com -q                 # بدون شاشة حية
