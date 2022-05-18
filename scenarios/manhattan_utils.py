#!/usr/bin/env python
"""

"""

from api_sumo import SumoScenario,CarType,Vehicle,Flow,Route
from random import randint

__author__ = "Bryan Alexis Freire Viteri"
__version__ = "3.0"
__email__ = "bryanfv95@gmail.com"

def get_edges(i1,j1,i2,j2,rows,cols,straight,pedestrians):
    edgef = '{}.{}/{}.{}'.format
    edgef_ped_w = ':{}.{}_w{}'.format
    edgef_ped_c = ':{}.{}_c{}'.format

    s = []
    if pedestrians == False:
        if straight == True:
            if i1==i2:
                i = j2-j1 if j2>j1 else j1-j2
                d = 1 if j2 > j1 else -1
                s.append(edgef(i1,j1,i1,j1+d))
                for j in range(1,i):
                    s.append(edgef(i1,j1+d*j,i1,j1+(1+j)*d))
            elif j1==j2:
                j = i2-i1 if i2>i1 else i1-i2
                d = 1 if i2 > i1 else -1
                s.append(edgef(i1,j1,i1+d,j1))
                for i in range(1,j):
                    s.append(edgef(i1+d*i,j1,i1+d*(i+1),j1))
            else:
                if i1 == 0 or i1 == rows-1:
                    s.expand(getRoute(i1,j1,i2,j1,nrows,ncols).expand(getRoute(i2,j1,i2,j2,nrows,ncols)))
                else:
                    s.expand(getRoute(i1,j1,i1,j2,nrows,ncols).expand(getRoute(i1,j2,i2,j2,nrows,ncols)))
        else:
            # Primero comenzaremos con NW y SE
            if i1 == 0 or i1 == rows-1:
                d = 1 if i1 == 0 else -1

                prev_i = i1
                prev_j = j1

                # Avance recto hasta el brazo arm
                for i in range(i1,i2,d):
                    s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
    #                print(prev_i,prev_j,prev_i+d,prev_j)
                    prev_i += d
                # Ahora toca girar
                for i in range(j1,j2,-d):
                    s.append(edgef(prev_i,prev_j,prev_i,prev_j-d))
    #                print(prev_i,prev_j,prev_i,prev_j-d)
                    prev_j -= d

            # Ahora con WS y EN
            elif j1 == 0 or j1 == cols-1:
                d = 1 if j1 == 0 else -1

                prev_i = i1
                prev_j = j1

                # Primero avanzamos
                for i in range(j1,j2,d):
                    s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
    #                print(prev_i,prev_j,prev_i,prev_j+d)
                    prev_j += d

                # Ahora toca girar
                for i in range(i1,i2,d):
                    s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
    #                print(prev_i,prev_j,prev_i+d,prev_j)
                    prev_i += d
    else:
        # Turno de los peatones
        # Peatones con movimiento recto
        if straight == True:

            #Rutas WE y EW
            if i1==i2:
                d = 1 if j1 == 0 else -1
                w = 1 if d == -1 else 3
                prev_i = i1
                prev_j = j1

                # Avance recto
                for i in range(j1,j2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w))
                    s.append(edgef_ped_c(prev_i,prev_j+d,w-1))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w-1))
                    prev_j += d
                s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))

            #Rutas NS y SN
            else:
                d = 1 if i1 == 0 else -1
                w0 = 0 if d == 1 else 2
                w1 = 3 if d == 1 else 1
                prev_i = i1
                prev_j = j1

                # Avance recto
                for i in range(i1,i2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w0))
                    s.append(edgef_ped_c(prev_i+d,prev_j,w1))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w1))
                    prev_i += d
                # Ahora toca girar
                s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
        # Peatones con giros a la derecha
        else:
            # NW
            if i1 == 0 and j2 == 0:
                d = 1
                w0 = 0
                w1 = 3
                prev_i = i1
                prev_j = j1

                # Giro y Avance recto
                for i in range(i1,i2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w0))
                    s.append(edgef_ped_c(prev_i+d,prev_j,w1))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w1))
                    prev_i += d
                # Ahora toca girar
                s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                s.append(edgef_ped_w(prev_i+d,prev_j,w0))

                prev_i = prev_i+d
                prev_j = prev_j
                d = -1
                w = 1

                # Primero avanzamos
                for i in range(j1,j2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w))
                    s.append(edgef_ped_c(prev_i,prev_j+d,w-1))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w-1))
                    prev_j += d
                s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))

            # SE
            elif i1 == rows-1 and j2 == cols-1:
                d = -1
                w0 = 2
                w1 = 1
                prev_i = i1
                prev_j = j1

                # Giro y Avance recto
                for i in range(i1,i2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w0))
                    s.append(edgef_ped_c(prev_i+d,prev_j,w1))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w1))
                    prev_i += d
                # Ahora toca girar
                s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                s.append(edgef_ped_w(prev_i+d,prev_j,w0))

                prev_i = prev_i+d
                prev_j = prev_j
                d = 1
                w = 3

                # Primero avanzamos
                for i in range(j1,j2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w))
                    s.append(edgef_ped_c(prev_i,prev_j+d,w-1))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w-1))
                    prev_j += d
                s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))

            # WS
            elif j1 == 0 and i2 == rows-1:
                d = 1
                w = 3
                prev_i = i1
                prev_j = j1

                # Primero avanzamos
                for i in range(j1,j2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w))
                    s.append(edgef_ped_c(prev_i,prev_j+d,w-1))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w-1))
                    prev_j += d
                s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                s.append(edgef_ped_w(prev_i,prev_j+d,w))

                prev_i = prev_i
                prev_j = prev_j+d
                d = 1
                w0 = 0
                w1 = 3

                # Giro y Avance recto
                for i in range(i1,i2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w0))
                    s.append(edgef_ped_c(prev_i+d,prev_j,w1))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w1))
                    prev_i += d
                # Ahora toca girar
                s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))

            # EN
            elif j1 == cols-1 and i2 == 0:
                d = -1
                w = 1
                prev_i = i1
                prev_j = j1

                # Primero avanzamos
                for i in range(j1,j2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w))
                    s.append(edgef_ped_c(prev_i,prev_j+d,w-1))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w-1))
                    prev_j += d
                s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                s.append(edgef_ped_w(prev_i,prev_j+d,w))

                prev_i = prev_i
                prev_j = prev_j+d
                d = -1
                w0 = 2
                w1 = 1

                # Giro y Avance recto
                for i in range(i1,i2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w0))
                    s.append(edgef_ped_c(prev_i+d,prev_j,w1))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w1))
                    prev_i += d
                # Ahora toca girar
                s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))

            # NE
            elif i1 == 0 and j2 == cols-1:
                d = 1
                w0 = 0
                w1 = 3
                prev_i = i1
                prev_j = j1

                # Giro y Avance recto
                for i in range(i1,i2-1,d):
                    s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w0))
                    s.append(edgef_ped_c(prev_i+d,prev_j,w1))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w1))
                    prev_i += d
                s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                s.append(edgef_ped_w(prev_i+d,prev_j,w0))
                s.append(edgef_ped_c(prev_i+d,prev_j,w1))

                prev_i = prev_i+d
                prev_j = prev_j
                d = 1
                w = 3

                # Primero avanzamos
                for i in range(j1,j2,d):
                    s.append(edgef_ped_w(prev_i,prev_j,w))
                    s.append(edgef_ped_c(prev_i,prev_j,w-1))
                    s.append(edgef_ped_w(prev_i,prev_j,w-1))
                    s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                    prev_j += d

            # SW
            elif i1 == rows-1 and j2 == 0:
                d = -1
                w0 = 2
                w1 = 1
                prev_i = i1
                prev_j = j1

                # Giro y Avance recto
                for i in range(i1,i2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w0))
                    s.append(edgef_ped_c(prev_i+d,prev_j,w1))
                    s.append(edgef_ped_w(prev_i+d,prev_j,w1))
                    prev_i += d
                # Ahora toca girar
                s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                s.append(edgef_ped_w(prev_i+d,prev_j,w0))
                s.append(edgef_ped_c(prev_i+d,prev_j,w1))

                prev_i = prev_i+d
                prev_j = prev_j
                d = -1
                w = 1

                # Primero avanzamos
                for i in range(j1,j2,d):
                    s.append(edgef_ped_w(prev_i,prev_j,w))
                    s.append(edgef_ped_c(prev_i,prev_j,w-1))
                    s.append(edgef_ped_w(prev_i,prev_j,w-1))
                    s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                    prev_j += d

            # WN
            elif j1 == 0 and i2 == 0:
                d = 1
                w = 3
                prev_i = i1
                prev_j = j1

                # Primero avanzamos
                for i in range(j1,j2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w))
                    s.append(edgef_ped_c(prev_i,prev_j+d,w-1))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w-1))
                    prev_j += d
                s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                s.append(edgef_ped_w(prev_i,prev_j+d,w))
                s.append(edgef_ped_c(prev_i,prev_j+d,w-1))

                prev_i = prev_i
                prev_j = prev_j+d
                d = -1
                w0 = 2
                w1 = 1

                # Giro y Avance recto
                for i in range(i1,i2,d):
                    s.append(edgef_ped_w(prev_i,prev_j,w0))
                    s.append(edgef_ped_c(prev_i,prev_j,w1))
                    s.append(edgef_ped_w(prev_i,prev_j,w1))
                    s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                    prev_i += d

            # ES
            elif j1 == cols-1 and i2 == rows-1:
                d = -1
                w = 1
                prev_i = i1
                prev_j = j1

                # Primero avanzamos
                for i in range(j1,j2-d,d):
                    s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w))
                    s.append(edgef_ped_c(prev_i,prev_j+d,w-1))
                    s.append(edgef_ped_w(prev_i,prev_j+d,w-1))
                    prev_j += d
                s.append(edgef(prev_i,prev_j,prev_i,prev_j+d))
                s.append(edgef_ped_w(prev_i,prev_j+d,w))
                s.append(edgef_ped_c(prev_i,prev_j+d,w-1))

                prev_i = prev_i
                prev_j = prev_j+d
                d = 1
                w0 = 0
                w1 = 3

                # Giro y Avance recto
                for i in range(i1,i2,d):
                    s.append(edgef_ped_w(prev_i,prev_j,w0))
                    s.append(edgef_ped_c(prev_i,prev_j,w1))
                    s.append(edgef_ped_w(prev_i,prev_j,w1))
                    s.append(edgef(prev_i,prev_j,prev_i+d,prev_j))
                    prev_i += d
#

    return ' '.join(s)