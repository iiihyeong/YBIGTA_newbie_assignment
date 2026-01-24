import numpy as np


class MultiLayerPerceptron(object):
    def __init__(self, nn_input_dim, nn_hdim1, nn_hdim2, nn_hdim3, nn_output_dim, init="random"):
        """
        Descriptions:
            W1: First layer weights
            b1: First layer biases
            W2: Second layer weights
            b2: Second layer biases
            W3: Third layer weights
            b3: Third layer biases
            W4: Fourth layer weights
            b4: Fourth layer biases
        
        Args:
            nn_input_dim: (int) The dimension D of the input data.
            nn_hdim1: (int) The number of neurons in the hidden layer H1.
            nn_hdim2: (int) The number of neurons in the hidden layer H2.
            nn_hdim3: (int) The number of neurons in the hidden layer H3.
            nn_output_dim: (int) The number of classes C.
            init: (str) initialization method used, {'random', 'constant'}
        
        Returns:
            
        """
        # reset seed before start
        np.random.seed(0)
        self.model = {}

        if init == "random":
            self.model['W1'] = np.random.randn(nn_input_dim, nn_hdim1)
            self.model['b1'] = np.zeros((1, nn_hdim1))
            self.model['W2'] = np.random.randn(nn_hdim1, nn_hdim2)
            self.model['b2'] = np.zeros((1, nn_hdim2))
            self.model['W3'] = np.random.randn(nn_hdim2, nn_hdim3)
            self.model['b3'] = np.zeros((1, nn_hdim3))
            self.model['W4'] = np.random.randn(nn_hdim3, nn_output_dim)
            self.model['b4'] = np.zeros((1, nn_output_dim))

        elif init == "constant":
            self.model['W1'] = np.ones((nn_input_dim, nn_hdim1))
            self.model['b1'] = np.zeros((1, nn_hdim1))
            self.model['W2'] = np.ones((nn_hdim1, nn_hdim2))
            self.model['b2'] = np.zeros((1, nn_hdim2))
            self.model['W3'] = np.ones((nn_hdim2, nn_hdim3))
            self.model['b3'] = np.zeros((1, nn_hdim3))
            self.model['W4'] = np.ones((nn_hdim3, nn_output_dim))
            self.model['b4'] = np.zeros((1, nn_output_dim))

    def forward_propagation(self, X):
        """
        Forward pass of the network to compute the hidden layer features and classification scores. 
        
        Args:
            X: Input data of shape (N, D)
            
        Returns:
            y_hat: (numpy array) Array of shape (N,) giving the classification scores for X
            cache: (dict) Values needed to compute gradients
            
        """
        W1, b1, W2, b2, W3, b3, W4, b4 = self.model['W1'], self.model['b1'], self.model['W2'], self.model['b2'], self.model['W3'], self.model['b3'], self.model['W4'], self.model['b4']
        
        ### CODE HERE ###
        # 행렬 연산 후 activation function 적용
        # y_hat을 X.shape[0] 크기로 reshape해야한다.
        h1 = X @ W1 + b1
        z1 = relu(h1) # ReLU를 활성화 함수로 사용

        h2 = z1 @ W2 + b1
        z2 = relu(h2)

        h3 = z2 @ W3 + b1
        z3 =relu(h3)

        h4 = z3 @ W4 + b4
        y_hat = sigmoid(h4)
        y_hat = y_hat.reshape(-1)

        ############################
        
        assert y_hat.shape==(X.shape[0],), f"y_hat.shape is {y_hat.shape}. Reshape y_hat to {(X.shape[0],)}"
        cache = {'h1': h1, 'z1': z1, 'h2': h2, 'z2': z2, 'h3': h3, 'z3': z3, 'h4': h4, 'y_hat': y_hat}
    
        return y_hat, cache

    def back_propagation(self, cache, X, y, L2_norm=0.0):
        """
        Compute the gradients
        
        Args:
            cache: (dict) Values needed to compute gradients
            X: (numpy array) Input data of shape (N, D)
            y: (numpy array) Training labels (N, ) -> (N, 1)
            L2_norm: (int) L2 normalization coefficient
            
        Returns:
            grads: (dict) Dictionary mapping parameter names to gradients of model parameters
            
        """
        W1, b1, W2, b2, W3, b3, W4, b4 = self.model['W1'], self.model['b1'], self.model['W2'], self.model['b2'], self.model['W3'], self.model['b3'], self.model['W4'], self.model['b4']
        h1, z1, h2, z2, h3, z3, h4, y_hat = cache['h1'], cache['z1'], cache['h2'], cache['z2'], cache['h3'], cache['z3'], cache['h4'], cache['y_hat']
        
        # For matrix computation
        y = y.reshape(-1, 1)
        y_hat = y_hat.reshape(-1, 1)
        
        ############################################################
        # gradient 계산하는 과정
        dy_hat = (y_hat - y) / (y_hat * (1 - y_hat) + 1e-15)

        dh4 = dy_hat * y_hat * (1-y_hat) # sigmoid
        db4 = np.sum(dh4, axis=0) # add 
        dW4 = z3.T @ dh4 + 2 * L2_norm * W4 # multiply
        dz3 = dh4 @ W4.T # multiply
        
        ### CODE HERE ###
        # 'gradient 계산하는 과정'을 참고하여 gradient 계산
        # dh3, db3, dW3, dz2, dh2, db2, dW2, dz1, dh1, db1, dW1 계산

        # --- Layer 3 (Hidden Layer) ---
        # 1. 활성화 함수 미분 -> dz3 * 미분값 = Layer 3의 delta(dh3)
        dh3 = dz3 * (z3 > 0).astype(float)

        # 2. 파라미터 Gradient 계산
        db3 = np.sum(dh3, axis=0)
        dW3 = z2.T @ dh3 + 2 * L2_norm * W3# 입력(z2) @ 델타(dh3)

        # 3. 아래 레이어로 오차 전파
        dz2 = dh3 @ W3.T

        # --- Layer 2 (Hidden Layer) ---
        dh2 = dz2 * (z2 > 0).astype(float)
        db2 = np.sum(dh2, axis=0)
        dW2 = z1.T @ dh2 + 2 * L2_norm * W2 # 입력(z1) @ 델타(dh2)
        dz1 = dh2 @ W2.T

        # --- Layer 1 (Input Layer) ---
        dh1 = dz1 * (z1 > 0).astype(float)
        db1 = np.sum(dh1, axis=0)
        dW1 = X.T @ dh1 + 2 * L2_norm * W1  # 입력(X) @ 델타(dh1)
       
        ################
        ############################################################
        
        grads = dict()
        grads['dy_hat'] = dy_hat
        grads['dh4'] = dh4
        grads['dW4'] = dW4
        grads['db4'] = db4
        grads['dW3'] = dW3
        grads['db3'] = db3
        grads['dW2'] = dW2
        grads['db2'] = db2
        grads['dW1'] = dW1
        grads['db1'] = db1

        return grads

    
    def compute_loss(self, y_pred, y_true, L2_norm=0.0):
        """
        Descriptions:
            Evaluate the total loss on the dataset
        
        Args:
            y_pred: (numpy array) Predicted target (N,)
            y_true: (numpy array) Array of training labels (N,)
        
        Returns:
            loss: (float) Loss (data loss and regularization loss) for training samples.
        """
        W1, b1, W2, b2, W3, b3, W4, b4 = self.model['W1'], self.model['b1'], self.model['W2'], self.model['b2'], self.model['W3'], self.model['b3'], self.model['W4'], self.model['b4']
        
        log_loss = -np.sum(y_true * np.log(y_pred + 1e-15) + (1 - y_true) * np.log(1 - y_pred + 1e-15))
        l2_loss = L2_norm * (np.sum(W1**2) + np.sum(W2**2) + np.sum(W3**2) + np.sum(W4**2))
        total_loss = log_loss + l2_loss


        return total_loss
        

    def train(self, X_train, y_train, X_val=None, y_val=None, learning_rate=1e-3, L2_norm=0.0, epoch=20000, print_loss=True):
        """
        Descriptions:
            Train the neural network using gradient descent.
        
        Args:
            X_train: (numpy array) training data (N, D)
            X_val: (numpy array) validation data (N, D)
            y_train: (numpy array) training labels (N,)
            y_val: (numpy array) valiation labels (N,)
            y_pred: (numpy array) Predicted target (N,)
            learning_rate: (float) Scalar giving learning rate for optimization
            L2_norm: (float) Scalar giving regularization strength.
            epoch: (int) Number of epoch to take
            print_loss: (bool) if true print loss during optimization

        Returns:
            A dictionary giving statistics about the training process
        """

        loss_history = []
        train_acc_history = []
        val_acc_history = []
        
        for it in range(epoch):
            ### CODE HERE ###
            # Forward propagation 후에 loss 계산, 
            # Back propagation 수행 후에 gradient update

            y_hat, cache = self.forward_propagation(X_train)
            loss = self.compute_loss(y_hat, y_train, L2_norm)
            grad = self.back_propagation(cache, X_train, y_train, L2_norm)

            # Gradient update
            self.model['W1'] -= learning_rate * grad['dW1']
            self.model['b1'] -= learning_rate * grad['db1']
            self.model['W2'] -= learning_rate * grad['dW2']
            self.model['b2'] -= learning_rate * grad['db2']
            self.model['W3'] -= learning_rate * grad['dW3']
            self.model['b3'] -= learning_rate * grad['db3']
            self.model['W4'] -= learning_rate * grad['dW4']
            self.model['b4'] -= learning_rate * grad['db4']

            ################# 
            if (it+1) % 1000 == 0:
                loss_history.append(loss)

                y_train_pred = self.predict(X_train)
                train_acc = np.average(y_train==y_train_pred)
                train_acc_history.append(train_acc)
                
                if X_val is not None:
                    y_val_pred = self.predict(X_val)
                    val_acc = np.average(y_val==y_val_pred)
                    val_acc_history.append(val_acc)

            if print_loss and (it+1) % 1000 == 0:
                print(f"Loss (epoch {it+1}): {loss}")
 
        if X_val is not None:
            return {
                'loss_history': loss_history,
                'train_acc_history': train_acc_history,
                'val_acc_history': val_acc_history,
            }
        else:
            return {
                'loss_history': loss_history,
                'train_acc_history': train_acc_history,
            }

    def predict(self, X):
        ### CODE HERE ###
        # Binary classification이므로 0.5 이상이면 1, 아니면 0으로 예측
        y_hat, _ = self.forward_propagation(X)
        
        predictions = (y_hat >= 0.5).astype(int)


        ##################
        return predictions
    
      


def tanh(x):
    x = np.tanh(x)
    return x


def relu(x):
    ### CODE HERE ###
    return np.maximum(0, x)
    ############################
    return x


def leakyrelu(x):
    ### CODE HERE ###
    return np.maximum(0.01 * x, x)
    ############################
    return x 


def sigmoid(x):
    x = 1 / (1 + np.exp(-x))
    return x