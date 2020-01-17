import rasp_tool as tl
import features
import selectMode
import time
import motor

def main():
    #=========プログラム開始=========#
    EMG_dim = 100    #予測に使うデータの次元数
    ch_num = 5  #チャンネル数

    while(True):
        #========モードの判定=========#
        print("モードの確認　[0:サンプリング], [1:動かす]")

        mode = selectMode.selectMode(2)

        #========義手を動かす=========#
        if(mode):
            try:
                motor.motor(EMG_dim, ch_num)

            except(KeyboardInterrupt):
                continue                
        
        #========サンプリングとモデルの作成========#
        else:
            pose = []   #取得したデータのラベルを保存
            feature = []
            flag = 0  #十分なデータが集まったかどうかの判定
            
            data_num = 10000 #生データの次元数

            while(flag == 0):
                print("手の動作の確認　[脱力(0), 握る(1), 親指内転(2), 開く(3), 親指外転(4), その他(5)]")

                p = selectMode.selectMode(5)

                EMG = tl.getEmg(data_num, ch_num)   #生データ取得

                print("保存の確認 [0:no],[1:yes]")

                save_flag = selectMode.selectMode(2)
                
                if(save_flag == 1):
                    feature += features.features(EMG)    #特徴量作成
                    print(feature)
                    pose += [p]*48  #手の動作を選択
                    #feature += featureTest.featureTest("/home/pi/data/EMG_file_test_2019-12-06.csv", p)
                if(len(pose) == 48):
                    continue
                
                print("続けるかどうかの確認 [0:yes], [1:no]")

                flag = selectMode.selectMode(2)

            tl.model(feature, pose) #モデル作成

if __name__ == "__main__":
    main()