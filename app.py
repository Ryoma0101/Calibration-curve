import numpy as np
import matplotlib.pyplot as plt
import matplotlib_fontja
import streamlit as st
from scipy.optimize import curve_fit
from io import BytesIO

# Streamlitアプリの設定
st.title('吸光度 vs. 濃度の検量線グラフ')

# ユーザー入力
st.write('濃度と吸光度の値を入力してください:')
concentration_input = st.text_input('濃度 (カンマ区切り)', '0.1, 0.2, 0.3, 0.4, 0.5')
absorbance_input = st.text_input(
    '吸光度 (カンマ区切り)', '0.05, 0.10, 0.15, 0.20, 0.25')

graph_title = st.text_input('グラフのタイトル', '吸光度 vs. 濃度の検量線グラフ')
x_label = st.text_input('横軸のラベル', '濃度 (c)')
y_label = st.text_input('縦軸のラベル', '吸光度 (Abs)')
legend_label = st.text_input('凡例のラベル', 'データポイント')
legend_line = st.text_input('近似直線のラベル', '近似直線')
legend_position = st.selectbox('凡例の位置', ['自動', '右上', '右下', '左上', '左下'])
include_origin = st.checkbox('原点を通る直線にする', value=True)


def parse_input(input_str):
    """入力された文字列をfloat型のリストに変換"""
    return np.array([float(x.strip()) for x in input_str.split(',')])


def linear_model(x, k):
    """原点を通る直線のモデル"""
    return k * x


def fit_model(concentration, absorbance, include_origin=True):
    """データに基づいて直線をフィッティング"""
    if include_origin:
        popt, _ = curve_fit(linear_model, concentration, absorbance)
        return popt[0], 0
    else:
        return np.polyfit(concentration, absorbance, 1)


def plot_graph(concentration, absorbance, k, b=0):
    """グラフの描画"""
    plt.figure(figsize=(11.69, 8.27))
    plt.xlim(left=0, right=concentration.max() * 1.1)
    plt.ylim(bottom=0, top=absorbance.max() * 1.1)

    plt.scatter(concentration, absorbance, edgecolors='black', facecolors='white',
                label=legend_label if legend_label else None, marker='o', s=100, zorder=2)

    x_fit = np.linspace(0, plt.xlim()[1], 100)
    y_fit = k * x_fit + b
    plt.plot(x_fit, y_fit, color='black', linestyle='-',
             label=legend_line if legend_line else None, zorder=1)

    equation_text = f'y = {k:.3f} x' if include_origin else f'y = {k:.3f} x + {b:.3f}'
    plt.text(x_fit[-1] * 0.7, y_fit[-1] * 0.9,
             equation_text, color='black', fontsize=10)

    # ラベル、凡例、タイトル
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if legend_label or legend_line:
        plt.legend(loc={'右上': 'upper right', '右下': 'lower right',
                   '左上': 'upper left', '左下': 'lower left', '自動': 'best'}[legend_position])
    plt.subplots_adjust(bottom=0.2)
    plt.figtext(0.5, 0.05, graph_title, ha='center', fontsize=14)

    return plt


# 入力値を配列に変換し、例外処理
try:
    concentration = parse_input(concentration_input)
    absorbance = parse_input(absorbance_input)

    k, b = fit_model(concentration, absorbance, include_origin)

    # グラフの描画
    plot = plot_graph(concentration, absorbance, k, b)
    st.pyplot(plot)

    # グラフを画像でダウンロードするボタン
    buf = BytesIO()
    plot.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    st.download_button(label='グラフをダウンロード', data=buf,
                       file_name='calibration_curve.png', mime='image/png')

    # 吸光度から濃度を計算する機能
    st.write('吸光度から濃度を計算します:')
    absorbance_value = st.text_input('吸光度を入力してください', '')
    try:
        absorbance_value = float(absorbance_value)
        concentration_value = (absorbance_value - b) / \
            k if not include_origin else absorbance_value / k
        st.write(f'計算された濃度: {concentration_value:.3f}')
    except ValueError:
        st.error('吸光度を正しく入力してください。')

except ValueError:
    st.error('数値をカンマで区切って正しく入力してください。')