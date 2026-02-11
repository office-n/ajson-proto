# Evidence: AJSON Spec v0.2 Implementation
Timestamp: 2026-02-11T08:35:00+09:00 (JST)

## 概要
本日策定した `docs/spec/ajson_spec_v0_2_2026_02_11.md` に関する決定事項の根拠と、v0.1 からの変更点を記録する。
本Evidenceは、仕様書v0.2が正当なプロセスと安全基準に基づいて作成されたことを証明する。

## v0.2 における主要な決定事項

### 1. 添付ファイルの容量と管理
- **決定**: 最低保証 512MB/ファイル、プロジェクト全体 2.5TB。
- **理由**: 昨今のLLMContext Window拡大に伴い、RAGや長文解析の需要が増加しているため、従来の「MB単位」では実用に耐えない。
- **安全策**: SSOT (File System) への保存時にハッシュ値を計算・記録し、改竄を検知できるようにする。
- **非ゴール**: 現時点でのクラウドストレージ（S3等）への直接アップロード（プロトタイプ範囲外）。

### 1-A. 生産性キット (Worktree / SSOT Auto-Tasks / Approval Queue)
- **決定**:
  1. **Worktree運用**: `task_id` ごとに `git worktree` で作業領域を分離する。
  2. **自動タスク**: ローカル完結のLint/Test/SSOTチェックを導入する。
  3. **Approval Queue**: 承認プロセスを状態として標準化する。
- **理由**:
  - 並列開発時のファイル競合や環境汚染（混線）を物理的に防ぐため。
  - 毎朝の健全性確認（Sanity Check）を自動化し、品質劣化を防ぐため。
  - 将来的なモバイル承認アプリの実装に向けた、承認状態の標準化が必要なため。
- **安全策**:
  - Worktree削除時は証跡を優先し、失敗時はディレクトリを保持する。
  - 自動タスクのスケジューラは既定OFFとし、意図しないリソース消費を防ぐ。
  - Approval Queueは「破壊操作」検出時に強制的に割り込む。


### 2. RPAの再定義
- **決定**: 「AIアプリUI操作」を禁止し、「API連携」を主軸、「外部サービスRPA」を代替手段とする。
- **理由**:
  - UI操作（Selenium等）はDOM変更に極めて弱く、メンテナンスコストが肥大化するため。
  - APIは安定した契約に基づくため、信頼性が高い。
- **安全策**:
  - 外部サービスRPA利用時は、Allowlistによる接続先制限と、破壊的操作に対する承認ゲートを必須化。
  - CAPTCHA/2FA要求時は即座に停止するSOS機能を実装。
- **非ゴール**: ChatGPT/Gemini等のWeb UI操作機能の実装。

### 3. Local Workspace Connector (Antigravity相当)
- **決定**: プロトタイプ限定で、ローカルファイル操作を許可する。
- **理由**: クラウド環境がないオンプレミス/ローカル環境での有用性を検証するため。
- **安全策**:
  - 操作範囲を「作業ディレクトリ配下」に厳格に制限。
  - 削除操作は「Trash（ゴミ箱）」をデフォルトとし、完全削除には承認を要求。
  - 権限変更（chmod/chown）を禁止。

### 4. コスト構造の明文化
- **決定**: 開発費と運用費（固定・変動）の概算式を仕様に含める。
- **理由**: ビジネス利用（販売モデル）を想定した際、ROIの試算根拠が必要となるため。
- **安全策**: 具体的な金額は断言せず、参照元URLと計算式を示すに留める（価格変動リスク回避）。

## v0.1 からの差分要約
- **構造**: `README.md` に散在していた要件を体系的な仕様書として統合。
- **追加**:
  - 添付ファイル要件（具体的な容量）。
  - RPAの厳格な定義（UI操作の禁止）。
  - Local Workspace Connector（ファイル操作）。
  - コスト試算ロジック。
  - **生産性キット**: Worktree強制、SSOT自動タスク、Approval Queue標準化。
- **変更なし**:

  - Starship Architecture、状態遷移、基本ロール（Jarvis/Cody）、Allowlist/Denylistによる防御機構。

## 参照URL (Reference Only)
- [OpenAI Pricing](https://openai.com/pricing)
- [AWS EC2 Pricing](https://aws.amazon.com/ec2/pricing/)
- [Google Cloud Compute Pricing](https://cloud.google.com/compute/pricing)
- [GitHub Pricing](https://github.com/pricing)

以上
