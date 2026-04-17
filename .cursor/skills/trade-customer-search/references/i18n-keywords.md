# 客户类型多语言词库

> 用于把"产品 + 客户类型 + 国家"翻译成本地语言搜索词。
> 维护原则：每个语言至少给出 **2-3 个等义词**，提升召回；自带常见拼写变体。

## 适用语言映射

| 语言代码 | 适用国家 |
|---|---|
| EN | US, UK, CA, AU, NZ, IE, ZA, SG, IN, PH, MY, AE, NG（默认全球保底）|
| DE | DE, AT, CH（德语区）|
| ES | ES, MX, AR, CL, CO, PE, VE, EC, UY, BO, PY, CR, GT, DO, PR |
| FR | FR, BE, CH, LU, MC, CA-QC, MA, TN, DZ, SN, CI |
| IT | IT, CH-TI, SM, VA |
| PT | BR, PT, AO, MZ |
| NL | NL, BE-VL, SR |
| RU | RU, BY, KZ, UZ, KG, AZ, AM, MD |
| PL | PL |
| TR | TR |
| AR | AE, SA, EG, MA, KW, QA, OM, JO, LB, IQ |
| JP | JP |
| KO | KR |
| TH | TH |
| VI | VN |
| ID | ID |
| ZH-Hant | TW, HK |

> 城市级国家如 CH（瑞士）按地区分德/法/意三语切换；CA 按 EN/FR-QC 切换；BE 按 NL/FR 切换。

---

## 客户类型 × 语言矩阵

每个 cell 的多个等义词用 `|` 分隔。搜索时**遍历**这些词，每词一次查询。

| 客户类型 (内部) | EN | DE | ES | FR | IT | PT | NL | RU | PL | TR | AR | JP | KO | TH | VI | ID |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **distributor** | distributor \| dealer | Vertriebspartner \| Distributor \| Händler | distribuidor \| representante | distributeur \| revendeur agréé | distributore \| concessionario | distribuidor \| representante | distributeur \| dealer | дистрибьютор \| представитель | dystrybutor \| przedstawiciel | distribütör \| bayi | موزع \| وكيل | 代理店 \| ディストリビューター | 대리점 \| 디스트리뷰터 | ตัวแทนจำหน่าย \| ดิสทริบิวเตอร์ | nhà phân phối \| đại lý | distributor \| agen |
| **importer** | importer \| import company | Importeur \| Einführer | importador | importateur | importatore | importador | importeur | импортёр | importer | ithalatçı | مستورد | 輸入業者 \| 輸入会社 | 수입업자 | ผู้นำเข้า | nhà nhập khẩu | importir |
| **wholesaler** | wholesaler \| wholesale supplier | Großhändler \| Großhandel | mayorista \| distribuidor mayorista | grossiste | grossista | atacadista | groothandel | оптовик \| оптовая торговля | hurtownik \| hurtownia | toptancı | تاجر جملة \| موزع بالجملة | 卸売業者 \| 問屋 | 도매상 \| 도매업체 | ผู้ค้าส่ง | nhà bán buôn \| đại lý sỉ | grosir |
| **retailer** | retailer \| retail store | Einzelhändler \| Fachhandel | minorista \| tienda detallista | détaillant \| commerce de détail | dettagliante \| negozio | varejista \| loja | detailhandel \| winkel | розничный продавец \| магазин | sprzedawca detaliczny \| sklep | perakendeci \| mağaza | تاجر تجزئة \| متجر | 小売業者 \| 小売店 | 소매업자 \| 소매점 | ผู้ค้าปลีก \| ร้านค้า | nhà bán lẻ \| cửa hàng | pengecer \| toko |
| **dealer** | dealer \| reseller | Händler \| Wiederverkäufer | comerciante \| revendedor | revendeur \| commerçant | rivenditore | revendedor | dealer \| wederverkoper | продавец \| перекупщик | sprzedawca | satıcı \| galerici | تاجر | 販売店 \| ディーラー | 판매자 | ผู้แทนจำหน่าย | đại lý | dealer |
| **supplier** | supplier \| sourcing | Lieferant \| Zulieferer | proveedor | fournisseur | fornitore | fornecedor | leverancier | поставщик | dostawca | tedarikçi | مورد | 仕入先 \| サプライヤー | 공급업체 | ผู้จัดจำหน่าย | nhà cung cấp | pemasok \| supplier |
| **brand** | brand \| brand owner | Marke \| Markenhersteller | marca | marque | marca | marca | merk | бренд | marka | marka | علامة تجارية | ブランド | 브랜드 | แบรนด์ | thương hiệu | merek |
| **B2B platform** | B2B \| trade buyer | B2B \| Geschäftskunden | B2B \| compradores comerciales | B2B \| acheteurs professionnels | B2B \| acquirenti commerciali | B2B \| compradores comerciais | B2B zakelijke kopers | B2B \| оптовые покупатели | B2B kupcy biznesowi | B2B ticari alıcılar | B2B \| مشترون تجاريون | B2B \| 法人客 | B2B \| 기업 구매자 | B2B \| ผู้ซื้อธุรกิจ | B2B \| khách hàng doanh nghiệp | B2B \| pembeli bisnis |

---

## 通用辅助词（按语言）

用于组装高级查询，不是主词，但能提升精准度。

| 概念 | EN | DE | ES | FR | IT | PT | RU | JP |
|---|---|---|---|---|---|---|---|---|
| 联系我们 | contact us | Kontakt | contacto | contact | contatti | contato | контакты | お問い合わせ |
| 关于我们 | about us | über uns | sobre nosotros | à propos | chi siamo | sobre nós | о компании | 会社概要 |
| 招商/经销商招募 | become a dealer \| dealer wanted | Händler werden \| Vertriebspartner gesucht | distribuidor solicitado | devenir revendeur | diventa rivenditore | seja revendedor | стать дилером | 代理店募集 |
| 询价/报价 | request a quote \| RFQ | Angebot anfordern | solicitar presupuesto | demande de devis | richiedi preventivo | solicitar orçamento | запросить цену | 見積依頼 |
| 批发/采购 | wholesale inquiry | Großhandelsanfrage | consulta de mayoreo | demande de gros | richiesta all'ingrosso | atacado | оптовый запрос | 卸売り問い合わせ |
| 进口商目录 | importers directory | Importeursverzeichnis | directorio de importadores | annuaire importateurs | elenco importatori | diretório de importadores | каталог импортёров | 輸入業者一覧 |

---

## 国家 → 默认搜索语言

```yaml
# 单语国家
DE: [de, en]
AT: [de, en]
FR: [fr, en]
IT: [it, en]
ES: [es, en]
PT: [pt, en]
NL: [nl, en]
PL: [pl, en]
RU: [ru, en]
TR: [tr, en]
JP: [jp, en]
KR: [ko, en]
TH: [th, en]
VN: [vi, en]
ID: [id, en]
BR: [pt, en]
MX: [es, en]
AR: [es, en]

# 多语种国家
CH: [de, fr, it, en]
BE: [nl, fr, en]
CA: [en, fr]

# 阿语区
AE: [ar, en]
SA: [ar, en]
EG: [ar, en]

# 英语为主
US: [en]
UK: [en]
AU: [en]
NZ: [en]
IN: [en]
SG: [en]
IE: [en]
ZA: [en]
PH: [en]
MY: [en]

# 默认未列国家
DEFAULT: [en]
```

---

## 使用示例

### 输入
```yaml
product: "硅胶宠物碗"
target_market: "DE"
customer_type: "wholesaler"
```

### 自动生成的查询（5-7 条）

```
Großhändler "Silikon Hundenapf"
Großhandel "Silikon Tiernapf"
silicone pet bowl wholesaler Germany
B2B Tierbedarf Großhandel "Silikon"
Tierfachhandel "Silikon" Lieferant
silicone dog bowl supplier .de
distributor Tierbedarf "Silikon"
```

### 输入
```yaml
product: "silk scarf"
target_market: "JP"
customer_type: ["retailer", "wholesaler"]
```

### 自動生成查詢

```
シルクスカーフ 卸売業者
絹スカーフ 問屋
silk scarf wholesaler Japan
シルクスカーフ 小売店
絹のスカーフ セレクトショップ
high-end silk scarf retailer Tokyo
```

---

## 维护说明

- 新增语言时，至少补全 6 个核心客户类型
- 等义词原则：1 个直译 + 1 个本地常用 + 可选 1 个口语化
- 行业类（如 "宠物用品"、"家居" 等）**不进本词库**，由调用方根据产品 i18n 翻译后传入
