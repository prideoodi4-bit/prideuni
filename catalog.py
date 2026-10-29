"""Deterministic catalog; unknown information never becomes eligibility or a zero fee."""
import json,re,copy
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).parent
NOTE='(هاي الأقساط الرسمية المذكورة، ممكن الجامعة تسوي تخفيضات بسيطة بفترات معينة)'
BRANCHES=['علمي','احيائي','تطبيقي','ادبي','فنون','مهني']
def display(s):
 s=re.sub(r'\s+',' ',str(s or '').replace('ـ','')).strip()
 for a,b in [('خلقنيات','تقنيات'),('خلقني','تقني'),('خلكنولوجيا','تكنولوجيا'),('خلكرير','تكرير'),('احلياخل','الحيات'),('االخلص','الاتص'),('امل','الم'),('احل','الح'),('اجل','الج'),('اهل','اله'),('الرت','التر'),('الرب','البر'),('اجمل','المج'),('احملا','المحا'),('الكهراب','الكهربا'),('السيرباين','السيبراني'),('السيبراين','السيبراني'),('االلكرت','الإلكتر'),('االسنان','الأسنان'),('االشعة','الأشعة'),('االجهزة','الأجهزة'),('االمن','الأمن'),('االنكلي','الإنكلي'),('االعمال','الأعمال'),('االدارة','الإدارة'),('االعالم','الإعلام'),('االدلة','الأدلة'),('االصط','الاصط'),('فيزاي','فيزيا'),('رايض','رياض'),('التعهيل','التأهيل'),('الطيب','الطبي'),('اببل','بابل'),('كربالء','كربلاء'),('دايلى','ديالى'),('الميكاخلرونكس','الميكاترونكس'),('مخترب','مختبر'),('االتصاالت','الاتصالات'),('الاتصاالت','الاتصالات'),('امليكاخلرونكس','الميكاترونكس')]:s=s.replace(a,b)
 return s

def norm(s):
 s=display(s).translate(str.maketrans('أإآىةؤئ','ااايهوي'))
 s=s.replace('اال','الا').replace('العالج','العلاج').replace('الالعلاج','العلاج')
 s=s.replace('كلية','').replace('كليه','').replace('قسم','')
 return re.sub(r'[^\w]','',s)

def load(name):return json.loads((ROOT/'data'/name).read_text())
RULEFILE=load('private_rules.json');RULES={r['id']:r for r in RULEFILE['records']}
GOV=load('government.json');TUITION=load('tuition.json')
# Explicit aliases address synonymous names and PDF encoding, never fuzzy-match a threshold.
ALIASES={
 1:['الطب العام','الطب'],4:['التمريض'],6:['تقنيات الأشعة','تقنيات الاشعة والسونار'],8:['تقنيات العلاج الطبيعي والتأهيل الطبي','تقنيات التأهيل الطبي والعلاج الطبيعي'],16:['تقنيات البصريات','تقنيات البصريات وفحص البصر'],17:['تقنيات التجميل والليزر','تقنيات التجميل بالليزر'],21:['تقنيات الصيدلة'],22:['تقنيات البصريات'],24:['تقنيات الاشعة'],28:['تقنيات طب الطوارئ والاسعاف الفوري'],29:['تقنيات التجميل والليزر'],30:['هندسة النفط والغاز'],31:['الهندسة المعمارية'],33:['الهندسة الميكانيكية'],34:['هندسة البناء والانشاءات'],40:['تقنيات الهندسة الكهربائية','هندسة تقنيات الكهرباء'],42:['هندسة تقنيات الاستكشافات النفطية وحفر الابار'],45:['هندسة الطب الحياتي'],50:['هندسة الاتصالات'],52:['هندسة الحاسبات'],53:['هندسة الذكاء الاصطناعي'],66:['هندسة تقنيات الحاسبات'],70:['هندسة تقنيات ميكانيك القوى / فرع هندسة تقنيات التبريد والتكييف'],71:['هندسة تقنيات الطيران'],78:['هندسة تقنيات ميكانيك القوى'],79:['هندسة تقنيات الذكاء الاصطناعي'],84:['الادلة الجنائية'],86:['علوم الفيزياء الطبية'],88:['علوم الامن السيبراني','علوم الامن السيبراني والحوسبة السحابية'],89:['علوم الحاسوب','علوم الحاسبات'],98:['القانون'],102:['الاعلام','الاعلام الرقمي','الصحافة','العلاقات العامة','الاذاعة والتلفزيون','الاعلان والاتصال التسويقي الرقمي'],103:['العلوم السياسية','العلوم السياسية والدولية','علاقات دولية ودبلوماسية'],105:['المحاسبة','الادارة الصناعية','ادارة وتسويق النفط والغاز','ادارة الاعمال','ادارة التسويق','ادارة المشاريع','ادارة المخاطر','ادارة الاستثمار والاعمال','الرقابة المحاسبية','العلوم المالية والمصرفية','علوم مالية ومصرفية','علوم محاسبية ومصرفية','العلوم المالية والمصرفية الاسلامية','الاقتصاد','اقتصاديات النفط والغاز','علوم السياحة'],107:['تقنيات المحاسبة','تقنيات ادارة الاعمال','تقنيات التسويق والمبيعات الالكترونية'],108:['التربية / الرياضيات','التربية / الكيمياء','التربية / الفيزياء','التربية / الحاسبات','التربية / علوم الحياة','التربية / الجغرافية','التربية / اللغة العربية','التربية / التاريخ'],109:['الآداب / اللغة الانكليزية','الآداب / اللغة الفرنسية'],110:['الآداب / اللغة العربية'],119:['التربية البدنية وعلوم الرياضة'],120:['القانون'],121:['الاعلام','الاعلام الرقمي','الصحافة','العلاقات العامة','الاذاعة والتلفزيون','الاعلان والاتصال التسويقي الرقمي'],123:['العلوم السياسية','العلوم السياسية والدولية','علاقات دولية ودبلوماسية'],124:['المحاسبة','الادارة الصناعية','ادارة وتسويق النفط والغاز','ادارة الاعمال','ادارة التسويق','ادارة المشاريع','ادارة المخاطر','ادارة الاستثمار والاعمال','الرقابة المحاسبية','العلوم المالية والمصرفية','علوم مالية ومصرفية','علوم محاسبية ومصرفية','العلوم المالية والمصرفية الاسلامية','الاقتصاد','اقتصاديات النفط والغاز'],125:['تقنيات المحاسبة','تقنيات ادارة الاعمال','تقنيات التسويق والمبيعات الالكترونية'],126:['الآداب / اللغة الانكليزية','الآداب / اللغة الفرنسية'],127:['الآداب / اللغة العربية'],128:['التربية / اللغة العربية','التربية / التاريخ','التربية / الجغرافية'],137:['التربية البدنية وعلوم الرياضة'],139:['الآداب / اللغة الفرنسية'],142:['التربية البدنية وعلوم الرياضة']}
ALIASES.setdefault(5,[]).append('تقنيات المختبرات الطبية')
ALIASES.setdefault(45,[]).append('هندسة الطب الحيات')
ALIASES.setdefault(67,[]).append('هندسة تقنيات الأجهزة الطبية')
ALIASES.setdefault(78,[]).append('هندسة تقنيات ميكاني القوى')
ALIASES.setdefault(86,[]).append('الفيزياء الطبية')
for n in [105,124]:ALIASES.setdefault(n,[]).extend(['ادارة اعمال','المالية والمصرفية'])
INDEX={}
for rid,r in RULES.items():
 n=int(rid.split('-')[1]);institute=21<=n<=29
 text=display(r['program_source'])
 values=[text]+text.split('/')+ALIASES.get(n,[])
 for val in values:
  key=norm(val)
  if len(key)>5 and key not in [norm('معهد'),norm('العلوم'),norm('الطبية'),norm('ادارة')]:INDEX.setdefault((institute,key),set()).add(rid)

def rule_ids(r):
 inst=r['institution_name'].startswith('معهد');keys=[norm(r['program_source']),norm(r['program_display'])]
 college=display(r.get('college_source') or '')
 if 'تربية' in college:keys+=[norm('التربية / '+r['program_display'])]
 if 'آداب' in college or 'اداب' in college:keys+=[norm('الآداب / '+r['program_display'])]
 result=set()
 for k in keys:result.update(INDEX.get((inst,k),set()))
 return sorted(result)

PROVINCES=['بغداد','النجف','كربلاء','بابل','البصرة','نينوى','الأنبار','ديالى','كركوك','صلاح الدين','ذي قار','القادسية','واسط','المثنى','ميسان']
def province(text):
 key=norm(text)
 for p in PROVINCES:
  if norm(p) in key:return p
 for a,b in [('الكوفة','النجف'),('الموصل','نينوى'),('تكريت','صلاح الدين'),('الفلوجة','الأنبار'),('القادسيه','القادسية'),('الديوانية','القادسية'),('سومر','ذي قار'),('جابر بن حيان','النجف'),('النهرين','بغداد'),('المستنصرية','بغداد'),('العراقية','بغداد'),('ابن سينا','بغداد')]:
  if norm(a) in key:return b
 return 'غير محدد'

def category(s):
 s=norm(s)
 for cat,terms in [('صحي',['طب','صيدل','تمريض','تخدير','بصري','اشعه','علاج','تجميل','اسنان']),('هندسي',['هندس','عماره']),('تقنية وعلوم',['حاس','علوم','ذكاء','سيبر','فيز','كيمي','رياضيات']),('إدارة وقانون',['ادار','محاسب','قانون','اقتصاد','مصرف','سياس']),('تربية وآداب',['تربي','اداب','لغه','تاريخ','جغرافي','اعلام','فنون'])]:
  if any(norm(t) in s for t in terms):return cat
 return 'تخصصات أخرى'

CATALOG=[]
for r in GOV['records']:
 full=display(r['program_full']);CATALOG.append({'id':f"gov-{r['source_row']:04}",'sector':'government','year':'2026-2027','university':display(r['university']),'program':full.split('/',1)[-1],'province':province(full),'category':category(full.split('/',1)[-1]),'shift':'morning','branch':r['branch'],'gender':r['gender'],'minimum':r['minimum_average'],'tie_break':r['tie_break_score'],'rules':[],'fee':None,'admission_status':'historical_threshold','notes':['حد منشور للقبول المركزي؛ مطابقته ليست ضمان قبول.'],'source':{'file':'government','page':r['source_pdf_page']},'raw':r})
for r in TUITION['records']:
 uni=r['institution_name']+(' / '+r['branch'] if r['branch'] else '')
 p=province(r['branch'] or r['institution_heading_source'])
 for shift in ['morning','evening']:
  CATALOG.append({'id':r['id']+'-'+shift,'sector':'private','year':'2026-2027','university':uni,'program':display(r['program_display']),'province':p,'category':category(r['program_display']),'shift':shift,'gender':'انثى' if 'للبنات' in uni else 'مختلط','branch':None,'minimum':None,'rules':rule_ids(r),'fee':copy.deepcopy(r[shift]),'admission_status':r['admission_status'],'notes':r['notes'],'fee_note':NOTE,'source':{'file':'tuition','page':r['source_pdf_page']},'raw':r})
BASE={r['id']:r for r in CATALOG}

def fee_for(item,average):
 f=item.get('fee')
 if not f:return None
 f=copy.deepcopy(f)
 if f['status']!='conditional':return f
 amount=None;a=Decimal(str(average)) if average is not None else None
 key=item['raw']['id']
 if a is not None:
  if key=='fee-0234':amount=5000000 if a>=95 else 5500000 if 90<=a<=94 else None
  elif key in ['fee-0237','fee-0238']:amount=6500000 if a>=96 else 7500000 if 90<=a<=95 else None
  elif key in ['fee-0757','fee-0758','fee-0760']:amount=2000000 if a>=80 else 2500000
  elif key=='fee-0759':amount=2000000 if a>=80 else None
  elif key=='fee-1049':amount=6250000 if a>95 else 6750000 if a<95 else None
  elif key=='fee-1264':amount=5500000 if a>=93 else None
  elif key=='fee-1265':amount=5000000 if a>=93 else None
  elif key=='fee-1561':amount=6500000 if a>=95 else 8000000 if 90<=a<=94 else None
 f['amount_iqd']=amount;f['condition_resolved']=amount is not None
 return f

def evaluate(item,average=None,branch=None,gender=None):
 r={k:copy.deepcopy(v) for k,v in item.items() if k!='raw'};r['eligible']=None;r['reason']='أدخل معدلك وفرعك وجنسك للمقارنة';r['gap']=None
 r['fee']=fee_for(item,average)
 if item['admission_status']=='suspended_in_source' or (r['fee'] and r['fee']['status']=='admission_suspended'):r.update(eligible=False,reason='القبول موقوف بحسب الملف');return r
 if r['fee'] and r['fee']['status']=='not_offered':r.update(eligible=False,reason='لا توجد دراسة بهذا الدوام');return r
 if gender and item.get('gender') not in ['مختلط',None,gender]:r.update(eligible=False,reason='هذا الخيار مخصص لجنس آخر بحسب الملف');return r
 if not branch or average is None or not gender:return r
 if item['sector']=='government':
  if branch in ['احيائي','تطبيقي','مهني']:r.update(reason='هذا الملف لا يحدد مسار هذا الفرع؛ راجع ضوابط القبول');return r
  if item['branch']!=branch:r.update(eligible=False,reason='الفرع لا يطابق الحد المنشور');return r
  minimum=item['minimum']
 else:
  if branch=='مهني':r.update(reason='المهني يحتاج مطابقة اختصاص مناظر؛ لا نطبق زيادة درجتين على كل الأقسام');return r
  if not item['rules']:r.update(reason='ربط هذا القسم بحد التقديم يحتاج مراجعة');return r
  possible=[RULES[x] for x in item['rules'] if x in RULES and branch in RULEFILE['groups'][RULES[x]['group']]]
  vals={x['minimum_application_'+item['shift']] for x in possible}
  vals.discard(None)
  if not possible:r.update(eligible=False,reason='الفرع غير مشمول بالقواعد المرتبطة بهذا القسم');return r
  if len(vals)!=1:r.update(reason='حد التقديم غير محسوم لهذا الدوام');return r
  minimum=next(iter(vals));r['minimum']=minimum;r['rule_sources']=[{'file':'private_rules','page':x['source_pdf_page']} for x in possible]
 delta=Decimal(str(average))-Decimal(str(minimum));r['gap']=float(delta)
 r['eligible']=delta>=0
 r['reason']=('معدلك يحقق الحد المنشور' if item['sector']=='government' else 'معدلك يحقق حد التقديم') if delta>=0 else 'معدلك أقل من الحد المنشور'
 if delta==0 and item['sector']=='government':r['reason']+='؛ راجع شرط المفاضلة'
 return r
