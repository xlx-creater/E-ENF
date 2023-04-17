# [“Seeing” Electric Network Frequency from Events](https://xlx-creater.github.io/E-ENF/)

### [Project Page](https://xlx-creater.github.io/E-ENF/) | [Paper](https://arxiv.org/pdf) | [Data](https://whueducn-my.sharepoint.com/:f:/g/personal/2018302120267_whu_edu_cn/En7DQ7Sg-KhIjeHlphDd1sIBA7alS2xg6UqKfbWf0E-3Zg?e=9aDKcG)

<img src='https://github.com/xlx-creater/E-ENF/blob/main/Illustration.png'/> 

> [“Seeing” Electric Network Frequency from Events](https://xlx-creater.github.io/E-ENF/) 
>
>  [Lexuan Xu](https://scholar.google.com.hk/citations?hl=zh-CN&user=g3itm8IAAAAJ), [Guang Hua](https://ghua-ac.github.io/), [Haijian Zhang](https://scholar.google.com/citations?user=cEWbejoAAAAJ&hl=zh-CN&oi=ao), [Lei Yu](https://scholar.google.com/citations?user=Klc_GHUAAAAJ&hl=zh-CN), [Ning Qiao](https://scholar.google.com/citations?user=e7FIdOMAAAAJ&hl=zh-CN&oi=ao)
>
> IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR2023)


## Prepare Data

Download the datasets from [EV-ENFD](https://whueducn-my.sharepoint.com/:f:/g/personal/2018302120267_whu_edu_cn/En7DQ7Sg-KhIjeHlphDd1sIBA7alS2xg6UqKfbWf0E-3Zg?e=9aDKcG).


1. Place one or several raw event files in the '.aedat4' format under the three scenarios in EV-ENFD into the 'Events/Raw/'.
2. Run 'Event_Process/aedat4_unpack_without_flir.py' to decompress the '.aedat4' files in 'Raw', and save the results in 'Events/Unpacked'.
3. Replace 'Events/ENF_Reference' with the 'ENF_Reference' folder in EV-ENFD, where each '.wav' file contains grid voltage changes recorded by the transformer within an hour.



## Estimate Electric Network Frequency using E-ENF

<img src='https://github.com/xlx-creater/E-ENF/blob/main/GUI.png' />



## Citation

Please cite our work if you use the code.

```
@InProceedings{Xu2023seeing,
      title={“Seeing” Electric Network Frequency from Events},
      author={Lexuan, Xu and Guang, Hua and Haijian, Zhhang and Lei, Yu and Ning, Qiao},
      booktitle={Computer Vision and Pattern Recognition (CVPR)},
      year={2023}
}
```
