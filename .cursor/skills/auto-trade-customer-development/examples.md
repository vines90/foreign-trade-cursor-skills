# 示例

## 示例 1：宠物小家电开发德国市场

### 输入

- 公司：`Guangdong Leling Precision`
- 发件人：`LIYANG XU`
- 职位：`Foreign Trade Manager`
- 产品：`pet small appliances`
- 卖点：
  - `exclusive semiconductor cooling and heating technology`
  - `lightweight`
  - `compact`
  - `quiet`
- 目标市场：`Germany`

### 预期执行

1. 搜索德国的 `distributor/importer/wholesaler`
2. 输出 `10-20` 家候选公司
3. 对可研究公司做官网背调
4. 按评分规则筛出 `A/B/C`
5. 对 `A` 级客户自动生成并发送开发邮件

## 示例 2：如果目标客户类型未提供

默认使用：

- `distributor`
- `importer`
- `wholesaler`

并在结果中说明是按默认类型搜索。

## 示例 3：发送结果

最终结果应类似：

```markdown
# 外贸客户开发结果

## 1. 输入摘要
- 产品：pet small appliances
- 公司：Guangdong Leling Precision
- 目标市场：Germany

## 2. 搜索结果
- 候选公司数：12
- 进入背调数：8
- 高价值客户数：3

## 3. 高价值客户
| 公司 | 官网 | 邮箱 | 评级 | 是否已发送 |
|------|------|------|------|------|
| Company A | https://... | info@... | A | 是 |

## 4. 发信结果
- 已发送：3
- 仅生成草稿：4
- 未发送原因：邮箱缺失 / 匹配度不足
```
