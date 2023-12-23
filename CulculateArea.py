import ezdxf
import numpy as np
from ezdxf.enums import TextEntityAlignment


class DrawRectangle():
    def __init__(self, x_coord , y_coord):
        #merge x_coord & y_coord into one 2D array
        self.NewPoint = list(zip(x_coord,y_coord))
        self.NewPointArray = np.array(self.NewPoint)
        self.NewHorizon_X1X2Y = []
        self.Rectangle=[]
        
        #1. 先根據Y座標排序 2. 再根據X座標排序
        self.SortedPoint = sorted(self.NewPointArray, key=lambda x: (x[1], x[0]))

        #畫出所有橫邊
        for i in range(len(self.SortedPoint)-1):
            if self.SortedPoint[i][1]==self.SortedPoint[i+1][1]:
                row = [self.SortedPoint[i][0],self.SortedPoint[i+1][0],self.SortedPoint[i][1]]
                self.NewHorizon_X1X2Y.append(row)

        #所有橫邊根據x1排序，再根據x2排序，最後根據Y座標排序
        self.SortedNewHorizon_X1X2Y = sorted(self.NewHorizon_X1X2Y, key=lambda x: (x[0], x[1], x[2]))

        for i in range(len(self.SortedNewHorizon_X1X2Y)-1):
            if self.SortedNewHorizon_X1X2Y[i][0]==self.SortedNewHorizon_X1X2Y[i+1][0] and self.SortedNewHorizon_X1X2Y[i][1]==self.SortedNewHorizon_X1X2Y[i+1][1]:
                RectanglePnt=[self.SortedNewHorizon_X1X2Y[i][0],self.SortedNewHorizon_X1X2Y[i][1],self.SortedNewHorizon_X1X2Y[i][2],self.SortedNewHorizon_X1X2Y[i+1][2]]
                self.Rectangle.append(RectanglePnt)
        


# RecordHorizonEdge record XY value of starting and ending point of each horizon edge in polyline
def RecordHorizonEdge(x_coord =[], y_coord=[]):

    HorizonEdge_X1X2Y = []
    for i in range(len(y_coord)-1):
        if(y_coord[i]==y_coord[i+1]):
            row = [x_coord[i],x_coord[i+1],y_coord[i]]
            HorizonEdge_X1X2Y.append(row)

    return HorizonEdge_X1X2Y

# 输入CAD文件的路径
#input_file_path = input("请输入CAD文件的路径：")
input_file_path = "D:\code\CAD project\project2_culculate_area\CAD\example 1.dxf"

# 打开输入的CAD文件
doc = ezdxf.readfile(input_file_path)

# 获取模型空间
msp = doc.modelspace()


# 创建新图层 "Dimension"
doc.layers.new(name="Dimension")


# 遍历图层 "0" 中的所有聚合线实体，以外積的公式算出聚合線的面積 
for LWPOLYLINE in msp.query(f"LWPOLYLINE[layer=='0']"):
    print(LWPOLYLINE)
    
    
    #print(type(LWPOLYLINE.points))
    points = LWPOLYLINE.get_points()

    x_coordinates = [coord[0] for coord in points]
    x_coordinates = [round(num,3) for num in x_coordinates]  #小數點取到第3位
    average_x = sum(x_coordinates) / len(x_coordinates)

    y_coordinates = [coord[1] for coord in points]
    y_coordinates = [round(num,3) for num in y_coordinates]   #小數點取到第3位
    average_y = sum(y_coordinates) / len(y_coordinates)

    #step 1:
    cross_product=0.000
    for i in range(len(points)):
        #1.算外積面積
        if(i<=len(points)-3):
            p1=(x_coordinates[i],y_coordinates[i])
            p2=(x_coordinates[i+1],y_coordinates[i+1])

            x0=x_coordinates[0]
            x1=x_coordinates[i+1]
            x2=x_coordinates[i+2]
            y0=y_coordinates[0]
            y1=y_coordinates[i+1]
            y2=y_coordinates[i+2]
                
            s=0.5*((x1-x0)*(y2-y0)-(y1-y0)*(x2-x0))
            cross_product +=s

        #2.標示點的序號
        if(i<len(points)-1):
            msp.add_text(i+1,height=40).set_placement(
                (x_coordinates[i],y_coordinates[i]),
                align=TextEntityAlignment.MIDDLE_RIGHT
            )
        
    #找出多邊形中的橫線
    horizon = RecordHorizonEdge(x_coordinates,y_coordinates)

    #畫點順序為順時針
    if(cross_product<0):
        msp.add_text("順序:順時針",height=40).set_placement(
            (average_x,average_y),
            align=TextEntityAlignment.MIDDLE_RIGHT
        )
        
        for i in range(len(x_coordinates)):

            OP=0.000 #step0: 先定義外積參數，

            #step1: 從i-1, i, i+1 三個點的向量變化判斷i點是否為凹點
            if i==0:
                v1_x=x_coordinates[i]-x_coordinates[len(x_coordinates)-2]
                v1_y=y_coordinates[i]-y_coordinates[len(x_coordinates)-2]
                v2_x=x_coordinates[i+1]-x_coordinates[i]
                v2_y=y_coordinates[i+1]-y_coordinates[i]
                OP=(v1_x*v2_y)-(v1_y*v2_x)
            elif i==(len(x_coordinates)-1):
                pass
            else:
                v1_x=x_coordinates[i]-x_coordinates[i-1]
                v1_y=y_coordinates[i]-y_coordinates[i-1]
                v2_x=x_coordinates[i+1]-x_coordinates[i]
                v2_y=y_coordinates[i+1]-y_coordinates[i]
                OP=(v1_x*v2_y)-(v1_y*v2_x)

            #step2: 順時針時，OP>0為凹點。找到凹點時，看v1_y和v2_y哪個絕對值>0
            if OP>0:
                compare_num = i
                if (abs(v1_y))>0:
                    #i-1點到i點是垂直向
                    compare_num = i-1
                else:
                    #i點到i+1點是垂直向
                    compare_num = i+1

                #step3: 判斷新的垂直線要怎麼畫
                if(y_coordinates[i]<y_coordinates[compare_num]):
                    #i點在compare_num點的下面，新的垂直線往下長
                    for j in range(len(horizon)):
                        #開始找哪一條橫線在i點正下面
                        if horizon[j][0]<x_coordinates[i] and horizon[j][1]>x_coordinates[i] and horizon[j][2]<y_coordinates[i]:
                            x_coordinates.append(x_coordinates[i])
                            y_coordinates.append(horizon[j][2])
                            break
                else:
                    #i點在compare_num點的上面，新的垂直線往上長
                    for j in range(len(horizon)):
                        #開始找哪一條橫線在i點正上面
                        if horizon[j][0]<x_coordinates[i] and horizon[j][1]>x_coordinates[i] and horizon[j][2]>y_coordinates[i]:
                            x_coordinates.append(x_coordinates[i])
                            y_coordinates.append(horizon[j][2])
                            break

    #畫點順序為逆時針                      
    else:
        msp.add_text("順序:逆時針",height=40).set_placement(
            (average_x,average_y),
            align=TextEntityAlignment.MIDDLE_RIGHT
        )

        for i in range(len(x_coordinates)):

            OP=0.000 #step0: 先定義外積參數，

            #step1: 從i-1, i, i+1 三個點的向量變化判斷i點是否為凹點
            if i==0:
                v1_x=x_coordinates[i]-x_coordinates[len(x_coordinates)-2]
                v1_y=y_coordinates[i]-y_coordinates[len(x_coordinates)-2]
                v2_x=x_coordinates[i+1]-x_coordinates[i]
                v2_y=y_coordinates[i+1]-y_coordinates[i]
                OP=(v1_x*v2_y)-(v1_y*v2_x)
            elif i==(len(x_coordinates)-1):
                pass
            else:
                v1_x=x_coordinates[i]-x_coordinates[i-1]
                v1_y=y_coordinates[i]-y_coordinates[i-1]
                v2_x=x_coordinates[i+1]-x_coordinates[i]
                v2_y=y_coordinates[i+1]-y_coordinates[i]
                OP=(v1_x*v2_y)-(v1_y*v2_x)

            #step2: 逆時針時，OP<0為凹點。找到凹點時，看v1_y和v2_y哪個絕對值>0
            if OP<0:
                compare_num = i
                if (abs(v1_y))>0:
                    #i-1點到i點是垂直向
                    compare_num = i-1
                else:
                    #i點到i+1點是垂直向
                    compare_num = i+1

                #step3: 判斷新的垂直線要怎麼畫
                if(y_coordinates[i]<y_coordinates[compare_num]):
                    #i點在compare_num點的下面，新的垂直線往下長
                    for j in range(len(horizon)):
                        #開始找哪一條橫線在i點正下面
                        if horizon[j][0]<x_coordinates[i] and horizon[j][1]>x_coordinates[i] and horizon[j][2]<y_coordinates[i]:
                            x_coordinates.append(x_coordinates[i])
                            y_coordinates.append(horizon[j][2])
                            break
                else:
                    #i點在compare_num點的上面，新的垂直線往上長
                    for j in range(len(horizon)):
                        #開始找哪一條橫線在i點正上面
                        if horizon[j][0]<x_coordinates[i] and horizon[j][1]>x_coordinates[i] and horizon[j][2]>y_coordinates[i]:
                            x_coordinates.append(x_coordinates[i])
                            y_coordinates.append(horizon[j][2])
                            break

    #獲取矩形點座標
    GetRectangle = DrawRectangle(x_coordinates,y_coordinates)
    RectanglePoint = GetRectangle.Rectangle

    for i in range(len(RectanglePoint)):
            TmpPoint=[(RectanglePoint[i][0],RectanglePoint[i][2]),
                      (RectanglePoint[i][1],RectanglePoint[i][2]),
                      (RectanglePoint[i][1],RectanglePoint[i][3]),
                      (RectanglePoint[i][0],RectanglePoint[i][3]),
                      (RectanglePoint[i][0],RectanglePoint[i][2])]
            msp.add_lwpolyline(TmpPoint)

    print(str(LWPOLYLINE)+"已處理完畢\n\n")




# 构造新文件名
file_name_parts = input_file_path.split('.')
output_file_path = file_name_parts[0] + "_DrawArea.dxf"

# 保存新文件
doc.saveas(output_file_path)

print(f"文件已保存为 {output_file_path}")