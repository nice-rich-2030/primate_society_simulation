# Statistics Panel Design Specification

## Overview
右側の情報パネルを拡張し、3種族（Gorilla, Chimp, Bonobo）の戦略確率分布を視覚的に表示する統計パネルを実装する。

## Requirements

### 1. Panel Layout
- **位置**: 画面右側の既存情報パネルを横に拡張
- **推奨サイズ**: 幅 300-400px（現在の情報パネルに追加）
- **背景色**: 半透明の暗色背景（既存UIと統一）

### 2. Statistics Display Structure

#### 2.1 表示する戦略カテゴリ（3カテゴリ）
1. **Foraging（食料探索）**: 4つの戦略
   - WideView
   - FastMove
   - RandomWalk
   - Ambush

2. **Combat（戦闘）**: 3つの戦略
   - Aggressive
   - Defensive
   - Group

3. **Flee（逃走）**: 3つの戦略
   - Speed
   - Hide
   - Scatter

#### 2.2 表示形式
- **合計バー数**: 30本（10戦略（3カテゴリ） × 3種族、以下の構造で表示）
- **構造**:
  ```
  [Foraging Strategies]
  WideView:    [Gorilla bar] [Chimp bar] [Bonobo bar]
  FastMove:    [Gorilla bar] [Chimp bar] [Bonobo bar]
  RandomWalk:  [Gorilla bar] [Chimp bar] [Bonobo bar]
  Ambush:      [Gorilla bar] [Chimp bar] [Bonobo bar]

  [Combat Strategies]
  Aggressive:  [Gorilla bar] [Chimp bar] [Bonobo bar]
  Defensive:   [Gorilla bar] [Chimp bar] [Bonobo bar]
  Group:       [Gorilla bar] [Chimp bar] [Bonobo bar]

  [Flee Strategies]
  Speed:       [Gorilla bar] [Chimp bar] [Bonobo bar]
  Hide:        [Gorilla bar] [Chimp bar] [Bonobo bar]
  Scatter:     [Gorilla bar] [Chimp bar] [Bonobo bar]
  ```

### 3. Data Calculation

#### 3.1 種族ごとの確率分布の計算
```python
# 各種族の全個体の戦略確率を平均化
species_avg_probabilities = {
    'Gorilla': {
        'foraging': {'WideView': 0.0, 'FastMove': 0.0, ...},
        'combat': {'Aggressive': 0.0, ...},
        'flee': {'Speed': 0.0, ...}
    },
    'Chimp': {...},
    'Bonobo': {...}
}

# 計算ロジック:
for species in ['Gorilla', 'Chimp', 'Bonobo']:
    agents_of_species = [a for a in agents if a.species == species]
    if len(agents_of_species) > 0:
        for context in ['foraging', 'combat', 'flee']:
            for strategy in strategies[context]:
                avg_prob = sum(agent.strategy_probs[context][strategy]
                              for agent in agents_of_species) / len(agents_of_species)
                species_avg_probabilities[species][context][strategy] = avg_prob
```

#### 3.2 更新頻度
- **更新間隔**: N フレームに1回
- **初期値**: N = 10
- **設定可能**: config.pyで`STATS_UPDATE_INTERVAL = 10`として定義
- **実装**: フレームカウンターを使用
  ```python
  if frame_count % STATS_UPDATE_INTERVAL == 0:
      update_statistics()
  ```

### 4. Visual Design

#### 4.1 Color Scheme
- **Gorilla**: 赤系（既存の種族色と統一）
  - Primary: `(180, 50, 50)`
  - Bar fill: `(200, 70, 70)`
- **Chimp**: 青系
  - Primary: `(50, 100, 180)`
  - Bar fill: `(70, 120, 200)`
- **Bonobo**: 緑系
  - Primary: `(50, 180, 50)`
  - Bar fill: `(70, 200, 70)`

#### 4.2 Bar Chart Design
```
戦略名        0%           25%          50%          75%         100%
WideView:     |████████████|            |            |            |  Gorilla
              |██████|                  |            |            |  Chimp
              |███████████████|         |            |            |  Bonobo
```

**各バーの仕様**:
- **高さ**: 8-10px
- **間隔**: 2-3px（種族間）、10px（戦略間）
- **境界線**: 1px、種族色の暗色版
- **背景グリッド**: 25%刻みの縦線（薄いグレー）
- **パーセンテージ表示**: バー右端に数値表示（例: "45%"）

#### 4.3 Section Headers
各カテゴリにヘッダーを表示:
```
┌─────────────────────────────────────┐
│     FORAGING STRATEGIES             │
├─────────────────────────────────────┤
│ [bars...]                           │
└─────────────────────────────────────┘
```

### 5. Layout Specification

#### 5.1 画面分割
```
┌──────────────────────────────────────────────────────────┐
│                   Simulation Area                         │
│                      (800x600)                            │
│                                                           │
├─────────────────────────────┬─────────────────────────────┤
│   Existing Info Panel       │   Statistics Panel          │
│   (200px width)             │   (300-400px width)         │
│   - Population              │   - Strategy Distributions  │
│   - Actions                 │   - By Species              │
│   - Selected Agent          │   - 3 Categories            │
│   - FPS                     │   - Real-time Updates       │
└─────────────────────────────┴─────────────────────────────┘
```

**推奨ウィンドウサイズ調整**:
- 現在: 800x600 (simulation) + 200 (panel) = 1000x600
- 新規: 800x600 (simulation) + 200 (info) + 350 (stats) = **1350x600**

#### 5.2 Statistics Panel Internal Layout
```
┌─────────────────────────────────────┐
│     STRATEGY STATISTICS             │  ← Title
│  Updated every 10 frames            │  ← Update info
├─────────────────────────────────────┤
│                                     │
│     FORAGING                        │  ← Category 1
│  WideView    [███] [██] [████]      │
│              45%   23%  58%         │
│  FastMove    [█] [████] [██]        │
│              12%  51%   28%         │
│  RandomWalk  [██] [██] [██]         │
│              25%  26%   24%         │
│  Ambush      [███] [█] [█]          │
│              38%  10%   18%         │
│                                     │
│      COMBAT                         │  ← Category 2
│  Aggressive  [████] [██] [█]        │
│              55%   28%  15%         │
│  Defensive   [██] [███] [████]      │
│              25%  42%   60%         │
│  Group       [█] [██] [██]          │
│              20%  30%   25%         │
│                                     │
│     FLEE                            │  ← Category 3
│  Speed       [███] [████] [██]      │
│              40%   55%   30%        │
│  Hide        [██] [█] [███]         │
│              30%  15%   45%         │
│  Scatter     [██] [██] [██]         │
│              30%  30%   25%         │
│                                     │
│  Legend: 🔴 Gorilla 🔵 Chimp 🟢 Bonobo │
└─────────────────────────────────────┘
```

### 6. Implementation Details

#### 6.1 New Configuration (config.py)
```python
# Statistics Panel Settings
STATS_PANEL_WIDTH = 350
STATS_UPDATE_INTERVAL = 10  # Update every N frames
STATS_BAR_HEIGHT = 8
STATS_BAR_SPACING = 2
STATS_STRATEGY_SPACING = 10
STATS_CATEGORY_SPACING = 20
STATS_SHOW_PERCENTAGES = True
STATS_SHOW_GRID = True
```

#### 6.2 New Class: StatisticsPanel (ui.py)
```python
class StatisticsPanel:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.update_interval = STATS_UPDATE_INTERVAL
        self.frame_counter = 0
        self.species_stats = {}

    def update(self, agents):
        """Calculate average strategy probabilities per species"""
        self.frame_counter += 1
        if self.frame_counter % self.update_interval == 0:
            self._calculate_species_stats(agents)

    def _calculate_species_stats(self, agents):
        """Average strategy probabilities across all agents of each species"""
        # Implementation as described in 3.1
        pass

    def draw(self, surface):
        """Render the statistics panel with bar charts"""
        # Draw background
        # Draw title
        # For each category (foraging, combat, flee):
        #     Draw category header
        #     For each strategy:
        #         Draw strategy label
        #         For each species (Gorilla, Chimp, Bonobo):
        #             Draw colored bar
        #             Draw percentage text
        pass
```

#### 6.3 Modified Files
1. **config.py**: 新しい定数を追加
2. **ui.py**: StatisticsPanelクラスを追加
3. **main.py**:
   - ウィンドウサイズを1350x600に変更
   - StatisticsPanelインスタンスを作成
   - メインループでupdate/draw呼び出し

### 7. Performance Considerations

#### 7.1 Optimization
- **キャッシング**: N フレームごとに1回だけ計算
- **部分更新**: 種族が絶滅した場合、その計算をスキップ
- **描画最適化**: バーの長さが変わらない場合、再描画をスキップ可能

### 8. Testing Checklist

- [ ] 3種族の確率分布が正しく計算される
- [ ] N フレームごとに更新される（デフォルト10）
- [ ] 30本のバーが正しく配置される
- [ ] 種族色が正しく適用される
- [ ] パーセンテージ表示が正確
- [ ] 種族が絶滅した場合でもエラーが発生しない
- [ ] パネルが画面に収まる
- [ ] パフォーマンス影響が最小限（60 FPS維持）

### 9. Future Enhancements (Phase 2+)

1. **グラフタイプの切り替え**: バーチャート ↔ ラインチャート（時系列）
2. **履歴トラッキング**: 確率分布の時間変化を記録・表示
3. **エクスポート機能**: 統計データをCSV/JSONで保存
4. **比較モード**: 特定の時点との比較表示
5. **フィルタリング**: 特定の戦略のみ表示

## Summary

この設計により、ユーザーは3種族の戦略適応状況をリアルタイムで視覚的に比較でき、強化学習の効果を直感的に理解できるようになる。種族ごとのバーを並べることで、各種族の戦略的傾向や学習パターンの違いが一目瞭然となる。
