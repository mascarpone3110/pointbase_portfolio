# PointBase  
AWSマルチアカウント構成で構築した、ポイント・注文管理Webアプリケーション

## 概要

PointBase は、学童施設・教育機関での利用を想定した
ポイント管理および注文管理 Web アプリケーションです。

単なる CRUD アプリではなく、

- セキュリティを前提とした認証設計
- 管理者／一般ユーザーのロール分離
- 業務アプリにおける注文・ステータス管理
- AWS マルチアカウント構成

を含め、本番運用を想定した設計で構築しています。

フロントエンドからバックエンド、インフラまでを一貫して設計・実装しました。

---

## 想定利用シーン

- 学童・教育施設でのポイント管理
- ポイントを利用した景品交換
- 管理者と一般ユーザーが存在する業務アプリケーション

業務システムに必要な権限分離・状態遷移設計を再現しています。


---

## 主な機能

### ユーザー・認証関連

- ユーザー登録
- ログイン / ログアウト
- JWT（Access / Refresh）認証
- HttpOnly + Secure 属性付き Cookie によるトークン管理
- CSRF 対策
- `/api/me/` による認証状態の再検証

### ポイント管理

- ポイント付与
- ポイント消費
- 保有ポイント確認

### カート・注文管理

- ポイント利用型カート機能
- 注文作成
- 注文履歴表示
- 注文ステータス管理  
  - 未交換（注文済み・未処理）  
  - 交換済み（管理者処理完了）

業務アプリケーションで必要となる
「状態遷移」を意識して設計しています。

### 権限管理

- 管理者 / 一般ユーザーのロール分離
- 管理者のみ実行可能な操作制御

- 管理者による注文ステータス更新

---

## 技術構成

### フロントエンド

- Next.js（App Router）

- TypeScript
- Tailwind CSS

### バックエンド

- Django
- Django REST Framework

### インフラ（AWS）

- ECS Fargate（APIコンテナ）
- Application Load Balancer
- CloudFront
- RDS
- S3
- IAM
- WAF
- GuardDuty
- SecurityHub
- CloudTrail

## AWS マルチアカウント構成

本プロジェクトは AWS Organizations を前提とした
マルチアカウント構成で設計しています。

![Multi Account](./images/multiaccount.png)

各アカウントの役割は以下の通りです。

- Management Account：組織管理・IAM Identity Center
- Production Account：本番環境（ECS / RDS）
- Security Account：SecurityHub / GuardDuty / Config
- Log Archive Account：CloudTrail・各種ログ集約
- Development Account：検証環境

ログおよびセキュリティ監視を分離し、
実務を想定したセキュアなアカウント設計を行っています。

---

## 認証・セキュリティ設計

本プロジェクトでは「動くこと」よりも
「安全に動くこと」を重視しています。

### 認証設計

- JWT（Access / Refresh）方式
- トークンは HttpOnly Cookie に保存
- JavaScript から直接取得不可
- 認証状態は `/api/me/` によりサーバー側で検証

### セキュリティ対策

- CSRF トークンによる二重送信対策
- CloudFront 経由のみ ALB に到達可能な構成
- AWS WAF による防御
- GuardDuty / SecurityHub による脅威検知
- CloudTrail による監査ログ管理

セキュリティを後付けにせず、設計段階から考慮しています。

---
## アーキテクチャ図
![AWS Architecture](./images/architecture.png)

CloudFront をエントリーポイントとし、
ALB 経由で Private Subnet 上の ECS (Fargate) に到達する構成としています。

RDS は Private Subnet に配置し、
アプリケーション経由のみアクセス可能とすることで
外部公開を防いでいます。

## 設計上の工夫

- 認証情報を localStorage に保存しない設計
- 業務アプリに近い注文・ステータス管理フローを再現
- マルチアカウントによるログ・監視の分離

- 将来的な Cognito 置き換えを前提とした設計

---

## 今後の改善予定

- Amazon Cognito への認証基盤移行
- Terraform による再現可能なインフラ構成
- RBAC の細分化
- 監査ログの強化
- CI/CD パイプライン整備
- テストコード追加

---

## 本プロジェクトで示したいこと

- 業務アプリケーションの設計理解
- 認証・認可・セキュリティを意識した実装力
- AWS を用いた本番想定構成の構築力

未経験からクラウドエンジニアを目指す中で、
実務レベルを意識した設計・構築に取り組みました。
