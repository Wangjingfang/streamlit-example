import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

st.header("st.write")
"""这是一个练习"""
# Example1
#
# 表情代码
# :smile: 代表微笑的表情
# :laughing: 代表大笑的表情
# :heart_eyes: 代表心形眼睛的表情
# :sob: 代表哭泣的表情
# :angry: 代表生气的表情
# :sunglasses: 代表太阳镜的表情
# :thumbsup: 代表点赞的表情
# :thumbsdown: 代表反对的表情
# :poop: 代表粪便的表情
# :ghost: 代表鬼魂的表情
#

st.markdown('Hello , *world!* :sunglasses:')
st.write('Hello, *World!* :angry:')
# Example2
st.write(1234)
st.text(1234)
st.markdown(123)
st.subheader(3456)
st.caption(2468)
st.latex(135)
st.code("import streamlit as st")

# Example3
df = pd.DataFrame({'first column':[1,2,3,4],'second column':[10,20,30,40]})
st.write(df)

# Example4
st.write('Below is a DataFrame:', df, 'Above is a dataframe.')

# Example5

df2 = pd.DataFrame(np.random.randn(200, 3),columns=['a','b','c'])

c = alt.Chart(df2).mark_circle().encode(x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])
st.write(c)