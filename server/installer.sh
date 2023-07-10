# Description: server installer

# Python librairies
pip install afinn
pip install attrdict3
pip install keras
pip install nltk
pip install numpy==1.22.3
pip install onnx==1.12.0
pip install opencv-python
pip install paddlepaddle
pip install paddlepaddle-gpu==2.4.2.post117 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
pip install paddleocr
pip install protobuf==3.19.6
pip install pyclipper
pip install scikit-learn==1.1.3
pip install scipy==1.8.1
pip install tensorflow==2.11.0
pip install tensorflow-gpu==2.11.0
pip install tensorflow-datasets==4.8.0
pip install tensorflow-metadata==1.12.0
pip install visualdl==2.4.2

# Depending repositories
git clone https://github.com/gstdenis-poly/UIED_custom ../../UIED_custom