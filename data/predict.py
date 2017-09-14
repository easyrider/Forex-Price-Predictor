
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
import lstm, time
import numpy as np
import getData2

def main(pair, timeframe):
	X_train, y_train, X_test, y_test = lstm.load_data(pair+'_'+timeframe+'_'+'history2.csv', 50, True)

	model = make_model(X_train, y_train)
	
	prediction = lstm.predict_point_by_point(model, X_test)
#	print "X_test"
#	print X_test
#	print y_test
#	print prediction

	print "Predictions"
	print prediction
	print "prediction[0]"
	print prediction[0]
	
	
	inputs = []
	i = 0
	for line in reversed(open(pair+'_'+timeframe+'_'+'history2.csv').readlines()):
		if i == 0:
			line.rstrip()  #ignoring since candle is incomplete
		else:
			inputs.append(float(line.rstrip()))
		i += 1
		if i == 51:
			break
	print "Inputs"
	print inputs
	inputs.reverse()
	#saving for denormalizing      
	p0 = float(inputs[0])
	inputs = [((float(p) / float(inputs[0])) - 1) for p in inputs]
	inputs = np.array(inputs)
	print "Normalized inputs"
	print inputs
	
	#possibly done wrong
	inputs = np.reshape(inputs, (1, 50, 1))
	print "Reshaped inputs"
	print inputs

	return model.predict(inputs ), p0

def make_model(X_train, y_train):
	model = Sequential()
	model.add(LSTM(input_dim=1, output_dim=50, return_sequences = True))
	model.add(Dropout(0.25))
	model.add(LSTM(100, return_sequences=False))
	model.add(Dropout(0.25))
	model.add(Dense(output_dim=1))
	model.add(Activation('linear'))
	start = time.time()
	model.compile(loss='mse', optimizer='rmsprop')
	print 'compilation time : ', time.time() - start
	model.fit(X_train, y_train, batch_size=512, nb_epoch=25, validation_split=0.05)
	return model

def predictNext(pair, timeframe):
	getData2.getData(pair, timeframe)
	predicted, p0 = main(pair, timeframe)
	print "predicted"
	print predicted
	print "De-Normalised prediction"  #pi = p0(ni + 1)
	denormalised = p0*(predicted[0][0] + 1)
	print denormalised
	return predicted[0][0], denormalised	

