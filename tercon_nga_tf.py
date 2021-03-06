########################################################################
# Calculate the territory control status from Hidden Markov Random Field
# Model. Each piece of territory has status between 0: full governmental
# conrol, and 1: full rebellion control
# With direct spatial and temporal relations, Country: Nigeria
# Written in Python 3
# exec(open("./tercon_nga_tf.py").read())
########################################################################
import pandas as pd
import numpy as np
import scipy as sp
import tensorflow as tf
import time

start = time.time()

########################################################################
# Read the files by Pandas and select the required columns
########################################################################

events_data = pd.read_csv('events_nganorthsmall_hex50.csv')
df_gt = pd.DataFrame(events_data, columns=["gid","year","type"])
df_gt["gid"] = df_gt["gid"].str.replace('nganorthsmallhex', '', case=False)
df_conv = df_gt.loc[df_gt['type'] == 'conventional']
df_terr = df_gt.loc[df_gt['type'] == 'terrorism']

print('No. Terrorism: ', len(df_terr), ', No. combat: ', len(df_conv))

df_conv = df_conv.as_matrix()
df_terr = df_terr.as_matrix()

########################################################################
# Feed the data into a tensor that represents the relations of space and time
########################################################################

r_span = 70
t_span = 7

xc = np.zeros((t_span,r_span))
for i in range(len(df_conv)):
	if int(df_conv[i,1]) >= 2009 and int(df_conv[i,1]) <= 2015:
		xc[int(df_conv[i,1] - 2009), int(df_conv[i,0]) - 1] += 1

xt = np.zeros((t_span,r_span))
for i in range(len(df_terr)):
	if int(df_terr[i,1]) >= 2009 and int(df_terr[i,1]) <= 2015:
		xt[int(df_terr[i,1] - 2009), int(df_terr[i,0]) - 1] += 1

print('Combat in each grid, avg: ', np.sum(xc)/r_span, ', max: ', np.max(xc))
print('Terror in each grid, avg: ', np.sum(xt)/r_span, ', max: ', np.max(xt))

########################################################################
# Construct the Tensorflow objective likelihood function to maximize
########################################################################

z = tf.Variable([[0 for i in range(r_span)] for j in range(t_span)], name='x', dtype=tf.float64)
z = tf.clip_by_value(z,0,1)

yc = tf.negative(tf.square(4*z - 2)) + 5
yt = tf.negative(tf.square(4*z - 1)) + 10

likelihood = tf.reduce_sum(tf.subtract(tf.multiply(xc, tf.log(yc)), yc) + tf.subtract(tf.multiply(xt, tf.log(yt)), yt))

for t in range(t_span):
	likelihood -= tf.reduce_sum(1 * tf.square(tf.subtract(tf.slice(z, [t, 0], [1, r_span-6]), tf.slice(z, [t, 6], [1, r_span-6]))))
	likelihood -= tf.reduce_sum(1 * tf.square(tf.subtract(tf.slice(z, [t, 0], [1, r_span-7]), tf.slice(z, [t, 7], [1, r_span-7]))))
	likelihood -= tf.reduce_sum(1 * tf.square(tf.subtract(tf.slice(z, [t, 0], [1, r_span-14]), tf.slice(z, [t, 14], [1, r_span-14]))))

for t in range(t_span - 1):
	likelihood -= tf.reduce_sum(1 * tf.square(tf.subtract(tf.slice(z, [t+1, 0], [1, r_span]), tf.slice(z, [t, 0], [1, r_span]))))

likelihood = tf.negative(likelihood)

########################################################################
# Define and run Tensorflow sessions
########################################################################

optimizer = tf.train.GradientDescentOptimizer(0.0001)
train = optimizer.minimize(likelihood)

init = tf.global_variables_initializer()

def optimize():
  with tf.Session() as session:
    session.run(init)
    session.run(z)
    print("Starting at", "Obj:", session.run(likelihood))
    for step in range(13000):
      session.run(train)
      session.run(z)
      print("Step", step, "Obj:", session.run(likelihood), end='\r')

    print("Step", step, "Obj:", session.run(likelihood))
    print(session.run(z))
    z_res = z.eval()
    outfile = open('./project.out','w')
    for t in range(t_span):
        for r in range(r_span):
            print(z_res[t,r], "\n", sep='', end='', file=outfile)
        print("\n", file=outfile)
    outfile.close()

optimize()

########################################################################
# Outpur and runtime report
########################################################################

time_used = time.time() - start
print('Completed in ', time_used, 'seconds.')
