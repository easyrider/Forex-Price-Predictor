
import predict

def update():
	pair = "USD_JPY"
	granularity = "H1"

	file = open("./"+pair+'_'+granularity+'_'+'predictions.csv', "a")
	prediction = predict.predictNext(pair, granularity)[1]
	file.write(str(prediction)+'\n')
