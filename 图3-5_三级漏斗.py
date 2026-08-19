# -*- coding: utf-8 -*-
"""
根据表11数据生成2030、2040、2050年环境合格供给三级漏斗图。

输出文件：
    table11_png/table11_2030.png
    table11_png/table11_2040.png
    table11_png/table11_2050.png

格式：PNG
分辨率：300 dpi
"""

import sys
import traceback
from pathlib import Path

import matplotlib

# 适用于无桌面环境、服务器和命令行运行。
# 必须在导入 pyplot 之前设置。
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Patch
from matplotlib.font_manager import fontManager
import os
for _fp in ['/usr/local/share/fonts/custom/NotoSansSC-Regular.ttf',
            '/usr/local/share/fonts/custom/NotoSansSC-Bold.ttf']:
    if os.path.exists(_fp):
        fontManager.addfont(_fp)


# ============================================================
# 1. 表11数据
# ============================================================
# 每组数据依次表示：
# 1. 名义需求
# 2. U口径气候合格
# 3. U口径双重合格
# 4. F口径气候合格
# 5. F口径双重合格
#
# 区间值使用：(下限, 上限)
# 单位：EJ
# ============================================================

DATA = {
    2030: {
        "B1": (0.09, 0.03, 0.03, 0.06, 0.06),
        "B2": (0.24, 0.09, 0.09, 0.17, 0.17),
        "B3": (0.38, 0.14, 0.14, 0.27, 0.27),
        "B4": (0.44, 0.17, 0.17, 0.31, 0.31),
    },
    2040: {
        "B1": (0.73, 0.28, 0.28, 0.51, 0.51),
        "B2": (1.95, 0.74, (0.50, 0.74), 1.37, 1.37),
        "B3": (3.17, 1.20, (0.50, 0.80), 2.22, (1.30, 2.19)),
        "B4": (3.66, 1.39, (0.50, 0.80), 2.56, (1.30, 2.19)),
    },
    2050: {
        "B1": (1.71, 0.65, (0.50, 0.65), 1.20, 1.20),
        "B2": (4.56, 1.73, (0.50, 0.80), 3.19, (2.00, 2.19)),
        "B3": (7.40, 2.81, (0.50, 0.80), 5.18, (2.00, 2.19)),
        "B4": (8.54, 3.25, (0.50, 0.80), 5.98, (2.00, 2.19)),
    },
}

SCENARIOS = ["B1", "B2", "B3", "B4"]
YEARS = [2030, 2040, 2050]


# ============================================================
# 2. 配色
# ============================================================
# 柱体和图例统一从该字典取色，确保颜色标注一致。
COLORS = {
    "nominal": "#7C878D",   # 名义需求：灰色
    "climate": "#39728A",   # 气候合格：蓝色
    "u_double": "#B45F52",  # U双重合格：红色
    "f_double": "#4E8A72",  # F双重合格：绿色
    "text": "#263238",
    "muted": "#65727A",
    "line": "#D7DEE1",
    "white": "#FFFFFF",
}


# ============================================================
# 3. 字体设置
# ============================================================
def select_font():
    """优先选择系统中可用的中文字体。"""
    candidates = [
        "Noto Sans CJK SC",
        "Noto Sans SC",
        "Source Han Sans CN",
        "Microsoft YaHei",
        "SimHei",
        "WenQuanYi Zen Hei",
        "Arial Unicode MS",
    ]

    installed_fonts = {font.name for font in fontManager.ttflist}

    for font_name in candidates:
        if font_name in installed_fonts:
            return font_name

    # 没有中文字体时程序仍可运行，但中文可能显示成方框。
    return "DejaVu Sans"


# ============================================================
# 4. 数值辅助函数
# ============================================================
def value_range(value):
    """将单值或区间值转换为浮点型下限、上限。"""
    if isinstance(value, (tuple, list)):
        if len(value) != 2:
            raise ValueError(f"区间必须包含两个数值：{value}")

        low = float(value[0])
        high = float(value[1])
    else:
        low = float(value)
        high = float(value)

    if low < 0 or high < 0:
        raise ValueError(f"数据不能为负数：{value}")

    if low > high:
        raise ValueError(f"区间下限不能大于上限：{value}")

    return low, high


def value_text(value):
    """生成图中的数值标签。"""
    low, high = value_range(value)

    if abs(low - high) < 1e-12:
        return f"{low:.2f} EJ"

    return f"{low:.2f}–{high:.2f} EJ"


def validate_data():
    """在绘图前检查数据结构。"""
    for year in YEARS:
        if year not in DATA:
            raise KeyError(f"缺少{year}年数据")

        for scenario in SCENARIOS:
            if scenario not in DATA[year]:
                raise KeyError(f"缺少{year}年{scenario}数据")

            row = DATA[year][scenario]

            if len(row) != 5:
                raise ValueError(
                    f"{year}年{scenario}应包含5项数据，"
                    f"实际为{len(row)}项"
                )

            for value in row:
                value_range(value)


# ============================================================
# 5. 绘制单个三级漏斗
# ============================================================
def draw_funnel(
    ax,
    x,
    y_levels,
    nominal,
    climate,
    double_value,
    regime,
    label_side,
):
    """
    绘制一条三级漏斗。

    参数：
    label_side：
        "left"  表示窄柱数字放在漏斗左侧，用于U口径；
        "right" 表示窄柱数字放在漏斗右侧，用于F口径。

    每层宽度相对于同一漏斗的名义需求计算。
    区间下限使用实色主体表示；区间上限使用半透明扩展表示。
    """
    if label_side not in ("left", "right"):
        raise ValueError("label_side只能是'left'或'right'")

    nominal_high = max(value_range(nominal)[1], 0.001)

    max_width = 1.36
    bar_height = 0.48

    # 外部数值与柱体边缘之间的间距。
    label_gap = 0.07

    def calculate_widths(value):
        low, high = value_range(value)
        return (
            max_width * low / nominal_high,
            max_width * high / nominal_high,
        )

    levels = [
        (nominal, COLORS["nominal"]),
        (climate, COLORS["climate"]),
        (double_value, COLORS[regime]),
    ]

    widths_by_level = [
        calculate_widths(value)
        for value, _ in levels
    ]

    # --------------------------------------------------------
    # 绘制层级之间的浅色连接面
    # --------------------------------------------------------
    for index in range(2):
        current_high = widths_by_level[index][1]
        next_high = widths_by_level[index + 1][1]

        y_top = y_levels[index] - bar_height / 2
        y_bottom = y_levels[index + 1] + bar_height / 2

        connector = Polygon(
            [
                (x - current_high / 2, y_top),
                (x + current_high / 2, y_top),
                (x + next_high / 2, y_bottom),
                (x - next_high / 2, y_bottom),
            ],
            closed=True,
            facecolor=levels[index + 1][1],
            edgecolor="none",
            alpha=0.12,
            zorder=1,
        )
        ax.add_patch(connector)

    # --------------------------------------------------------
    # 绘制三级主体和数值标签
    # --------------------------------------------------------
    for index, ((value, color), width_pair) in enumerate(
        zip(levels, widths_by_level)
    ):
        low_width, high_width = width_pair
        y = y_levels[index]

        # 区间上限：半透明背景。
        if high_width > low_width + 1e-12:
            upper_patch = Polygon(
                [
                    (x - high_width / 2, y + bar_height / 2),
                    (x + high_width / 2, y + bar_height / 2),
                    (x + high_width / 2, y - bar_height / 2),
                    (x - high_width / 2, y - bar_height / 2),
                ],
                closed=True,
                facecolor=color,
                edgecolor=color,
                linewidth=0.6,
                alpha=0.25,
                zorder=2,
            )
            ax.add_patch(upper_patch)

        # 区间下限或单值：实色主体。
        lower_patch = Polygon(
            [
                (x - low_width / 2, y + bar_height / 2),
                (x + low_width / 2, y + bar_height / 2),
                (x + low_width / 2, y - bar_height / 2),
                (x - low_width / 2, y - bar_height / 2),
            ],
            closed=True,
            facecolor=color,
            edgecolor=COLORS["white"],
            linewidth=0.9,
            zorder=3,
        )
        ax.add_patch(lower_patch)

        text = value_text(value)

        # 名义需求条最宽，数字始终放在柱体内部。
        # 其他层级只有足够宽时才放在内部。
        place_inside = index == 0 or low_width >= 0.80

        if place_inside:
            text_x = x
            text_color = COLORS["white"]
            horizontal_alignment = "center"
            font_weight = "bold"
        else:
            # 使用区间上限宽度确定外部标签位置，防止文字覆盖
            # 半透明的区间上限部分。
            visible_width = max(low_width, high_width)

            if label_side == "left":
                # U口径数字放在其漏斗左侧，不再偏向F漏斗。
                text_x = x - visible_width / 2 - label_gap
                horizontal_alignment = "right"
            else:
                # F口径数字放在其漏斗右侧。
                text_x = x + visible_width / 2 + label_gap
                horizontal_alignment = "left"

            text_color = COLORS["text"]
            font_weight = "normal"

        ax.text(
            text_x,
            y,
            text,
            ha=horizontal_alignment,
            va="center",
            fontsize=7.8,
            color=text_color,
            fontweight=font_weight,
            zorder=5,
            clip_on=False,
        )


# ============================================================
# 6. 生成单个年份的图片
# ============================================================
def draw_year(year, rows, output_dir):
    """生成指定年份的漏斗图。"""
    fig, ax = plt.subplots(figsize=(15.5, 8.5), dpi=500)

    # 增大四个情景中心之间的间距，避免相邻情景文字重叠。
    centers = {
        "B1": 0.00,
        "B2": 3.65,
        "B3": 7.30,
        "B4": 10.95,
    }

    y_levels = [2.25, 1.10, -0.05]

    # 同一情景内U/F漏斗之间的距离。
    # U在左侧，F在右侧。
    regime_offset = 0.76

    # 横向参考线。
    for y in [1.675, 0.525]:
        ax.axhline(
            y,
            color=COLORS["line"],
            linewidth=0.8,
            zorder=0,
        )

    for scenario in SCENARIOS:
        (
            nominal,
            u_climate,
            u_double,
            f_climate,
            f_double,
        ) = rows[scenario]

        center = centers[scenario]
        x_u = center - regime_offset
        x_f = center + regime_offset

        # U口径：窄柱数字放在漏斗左侧。
        draw_funnel(
            ax=ax,
            x=x_u,
            y_levels=y_levels,
            nominal=nominal,
            climate=u_climate,
            double_value=u_double,
            regime="u_double",
            label_side="left",
        )

        # F口径：窄柱数字放在漏斗右侧。
        draw_funnel(
            ax=ax,
            x=x_f,
            y_levels=y_levels,
            nominal=nominal,
            climate=f_climate,
            double_value=f_double,
            regime="f_double",
            label_side="right",
        )

        # U/F口径标签。
        ax.text(
            x_u,
            -0.58,
            "U 无约束",
            ha="center",
            va="top",
            fontsize=8.5,
            color=COLORS["muted"],
        )

        ax.text(
            x_f,
            -0.58,
            "F 防火墙",
            ha="center",
            va="top",
            fontsize=8.5,
            color=COLORS["muted"],
        )

        # B情景标签。
        ax.text(
            center,
            -0.87,
            scenario,
            ha="center",
            va="top",
            fontsize=13,
            fontweight="bold",
            color=COLORS["text"],
        )

    # --------------------------------------------------------
    # 左侧三级定义
    # --------------------------------------------------------
    left = -1.65

    level_labels = [
        (
            "一级：名义需求",
            "船用生物燃料名义需求规模",
            y_levels[0],
        ),
        (
            "二级：气候合格",
            "含ILUC强度低于94 gCO₂e/MJ\n且碳债偿还期不超过20年",
            y_levels[1],
        ),
        (
            "三级：双重合格",
            "叠加粮食安全、可追溯性\n与物理供给约束",
            y_levels[2],
        ),
    ]

    for title, subtitle, y in level_labels:
        ax.text(
            left,
            y + 0.04,
            title,
            ha="right",
            va="center",
            fontsize=10.2,
            fontweight="bold",
            color=COLORS["text"],
        )

        ax.text(
            left,
            y - 0.27,
            subtitle,
            ha="right",
            va="top",
            fontsize=7.7,
            color=COLORS["muted"],
            linespacing=1.25,
        )

    # --------------------------------------------------------
    # 标题和副标题
    # --------------------------------------------------------
    ax.text(
        0.5,
        1.08,
        f"{year}年环境合格供给三级漏斗",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=17,
        fontweight="bold",
        color=COLORS["text"],
    )

    ax.text(
        0.5,
        1.035,
        "表11中央判据｜单位：EJ｜半透明部分表示区间上限",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=9.5,
        color=COLORS["muted"],
    )

    # --------------------------------------------------------
    # 年份结论
    # --------------------------------------------------------
    if year == 2030:
        conclusion = (
            "2030年供给规模较小，双重合格量与气候合格量基本一致"
        )
    elif year == 2040:
        conclusion = (
            "2040年开始出现粮食安全与物理供给约束，U/F差异扩大"
        )
    else:
        conclusion = (
            "2050年双重合格供给受UCO与二代原料物理上限约束"
        )

    ax.text(
        0.5,
        -0.14,
        conclusion,
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=8.8,
        color=COLORS["muted"],
    )

    # --------------------------------------------------------
    # 图例
    # --------------------------------------------------------
    # 每个图例项目独立创建，确保颜色与柱体一致。
    legend_handles = [
        Patch(
            facecolor=COLORS["nominal"],
            edgecolor="none",
            label="名义需求",
        ),
        Patch(
            facecolor=COLORS["climate"],
            edgecolor="none",
            label="气候合格",
        ),
        Patch(
            facecolor=COLORS["u_double"],
            edgecolor="none",
            label="U口径双重合格",
        ),
        Patch(
            facecolor=COLORS["f_double"],
            edgecolor="none",
            label="F口径双重合格",
        ),
    ]

    ax.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.24),
        ncol=4,
        frameon=False,
        fontsize=8.5,
        handlelength=1.4,
        columnspacing=1.8,
    )

    # 增大坐标范围，保证B1的U侧数字和B4的F侧数字完整显示。
    ax.set_xlim(-3.10, 12.65)
    ax.set_ylim(-1.35, 2.85)
    ax.axis("off")

    output_path = output_dir / f"图{year // 10 - 200}_环境合格供给三级漏斗_{year}.png"

    fig.savefig(
        output_path,
        dpi=500,
        format="png",
        bbox_inches="tight",
        facecolor="white",
        edgecolor="none",
    )

    plt.close(fig)

    # 检查图片是否成功生成。
    if not output_path.exists():
        raise RuntimeError(f"图片未写入磁盘：{output_path}")

    if output_path.stat().st_size < 1000:
        raise RuntimeError(f"图片文件异常，大小过小：{output_path}")

    print(f"[完成] {output_path}")
    print(f"       大小：{output_path.stat().st_size / 1024:.1f} KB")


# ============================================================
# 7. 主程序
# ============================================================
def main():
    validate_data()

    # 同时兼容.py脚本和部分交互式运行环境。
    try:
        script_dir = Path(__file__).resolve().parent
    except NameError:
        script_dir = Path.cwd()

    output_dir = Path("/sandbox/workspace/revision_p2/figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    font_name = select_font()

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = [font_name, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    print(f"输出目录：{output_dir.resolve()}")
    print(f"使用字体：{font_name}")

    for year in YEARS:
        draw_year(year, DATA[year], output_dir)

    print()
    print("三张PNG图片已经生成：")
    for year in YEARS:
        print(f"  {output_dir / f'图{year // 10 - 200}_环境合格供给三级漏斗_{year}.png'}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print()
        print("图片生成失败，完整错误如下：")
        traceback.print_exc()
        sys.exit(1)
