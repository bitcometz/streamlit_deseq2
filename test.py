from streamlit import session_state as ss
import streamlit as st
import uuid

# Create de key
if 'dek' not in ss:
    ss.dek = str(uuid.uuid4())


def update_flag1():
    ss["click1"] = True

def update_flag2():
    ss["click2"] = True

if "list1" not in ss:
    ss["list0"]  = [1, 2, 3, 4, 5, 6]
    ss["list1"]  = [1, 2, 3, 4, 5, 6]
    ss["list2"]  = [1, 2, 3, 4, 5, 6]
    ss["flag1"]  = 1000
    ss["flag2"]  = 2000
    ss["click1"] = False
    ss["click2"] = False
    ss["group1"] = None
    ss["group2"] = None
    ss["index1"] = None
    ss["index2"] = None



st.write(ss["click1"])

ss["group1"] = st.selectbox(
    "group1",
    ss.list1,
    key=ss.flag1,
    index=ss.index1,
    placeholder="Please select ...",
    label_visibility="collapsed",
    on_change=update_flag1,
)

ss["group2"] = st.selectbox(
    "group2",
    ss.list2,
    key=ss.flag2,
    index=ss.index2,
    placeholder="Please select ...",
    label_visibility="collapsed",
    on_change=update_flag2,
)

ss["list1"]  = [i for i in ss["list0"] if i!= ss["group2"]]
ss["list2"]  = [i for i in ss["list0"] if i!= ss["group1"]]


### 难点在于选择了才变化
if ss["click1"]:
    if ss["group2"] != None:
        ss["index2"] = ss["list2"].index(ss["group2"])
    ss["flag2"] += 1

if ss["click2"]:
    if ss["group1"] != None:
        ss["index1"] = ss["list1"].index(ss["group1"])
    ss["flag1"] += 1

st.write(ss.list1)
st.write(ss.list2)


ss["click1"] = False
ss["click2"] = False








