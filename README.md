# [“Seeing” Electric Network Frequency from Events](https://xlx-creater.github.io/E-ENF/)

### [Project Page](https://xlx-creater.github.io/E-ENF/) | [Paper](https://arxiv.org/pdf/2305.02597.pdf) | [Data](https://whueducn-my.sharepoint.com/:f:/g/personal/2018302120267_whu_edu_cn/En7DQ7Sg-KhIjeHlphDd1sIBA7alS2xg6UqKfbWf0E-3Zg?e=9aDKcG)

<img src='https://github.com/xlx-creater/E-ENF/blob/main/Illustration.png'/> 

> [“Seeing” Electric Network Frequency from Events](https://xlx-creater.github.io/E-ENF/) 
>
>  [Lexuan Xu](https://scholar.google.com.hk/citations?hl=zh-CN&user=g3itm8IAAAAJ), [Guang Hua](https://ghua-ac.github.io/), [Haijian Zhang](https://scholar.google.com/citations?user=cEWbejoAAAAJ&hl=zh-CN&oi=ao), [Lei Yu](https://scholar.google.com/citations?user=Klc_GHUAAAAJ&hl=zh-CN), [Ning Qiao](https://scholar.google.com/citations?user=e7FIdOMAAAAJ&hl=zh-CN&oi=ao)
>
> IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR2023)


## Prepare Data

Download the datasets from [EV-ENFD](https://whueducn-my.sharepoint.com/:f:/g/personal/2018302120267_whu_edu_cn/En7DQ7Sg-KhIjeHlphDd1sIBA7alS2xg6UqKfbWf0E-3Zg?e=9aDKcG).


1. Place one or several raw event files in the '.aedat4' format under the three scenarios in EV-ENFD into the 'Events/Raw/'.
2. Run 'Event_Process/aedat4_unpack_without_flir.py' to unpack '.aedat4' files in 'Raw', and the result will be saved in 'Events/Unpacked/dvSave-'.
3. Replace 'Events/ENF_Reference' with the 'ENF_Reference' folder in EV-ENFD, where each '.wav' file contains grid voltage changes recorded by the transformer within an hour.


After performing the aforementioned operations, the contents of the 'Events' folder are as follows:
```
<project root>
  |-- Events
  |     |-- Raw
  |     |     |-- dvSave-2022_08_17_20_10_23.aedat4
  |     |     |-- dvSave-2022_08_17_20_24_41.aedat4
  |     |     |-- ...
  |     |-- Unpacked
  |     |     |-- dvSave-2022_08_17_20_10_23
  |     |     |    |-- events
  |     |     |    |-- event2ts
  |     |     |-- dvSave-2022_08_17_20_24_41
  |     |     |    |-- events
  |     |     |    |-- event2ts
  |     |     |-- ...     
  |     |-- ENF_Reference
  |     |     |-- 2022_08_17_Wed_17_00_00.wav
  |     |     |-- 2022_08_17_Wed_18_00_00.wav
```


## Estimate Electric Network Frequency using E-ENF

<img src='https://github.com/xlx-creater/E-ENF/blob/main/GUI.png' />

1. Run 'E_ENF/E_ENF(GUI)/ENF_match_GUI.py' to get the GUI interface shown above.
2. Click the 'Browser' button next to 'Open File' and select the event stream 'Events/Unpacked/dvSave-/events' you want to extract.
3. The 'Browser' button next to 'Reference Floder' select the 'Events/ENF_Reference' folder to get the real ground truth reference.
4. Under 'Possible begin and end time of recording' fill in the reference signal time range of the search, and click 'Generate Task' to check the selected range.
5. Click the 'Start Processing' button, the program will estimate the ENF signal from the event stream, and match the reference signal closest to the estimated result within the selected reference time range, and the result will be displayed in the lower right corner of the GUI.


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
