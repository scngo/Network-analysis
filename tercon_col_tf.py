########################################################################
# Calculate the territory control status from Hidden Markov Random Field
# Model. Each piece of territory has status between 0: full governmental
# conrol, and 1: full rebellion control
# With continuous spatial and temporal decays, Country: Colombia
# Written in Python 3
# exec(open("./tercon_col_tf.py").read())
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

events_data = pd.read_csv('events_decay_col_hex50_s40_t8.csv')
df_gt = pd.DataFrame(events_data, columns=["gid","timeindex","weighted_terrorism","weighted_combats"])
df_gt["gid"] = df_gt["gid"].str.replace('colhex', '', case=False)
df_gt = df_gt.convert_objects(convert_numeric=True)

print('Max Terrorism: ', max(df_gt["weighted_terrorism"]), ', Max combat: ', max(df_gt["weighted_combats"]))

r_span = 1488 # 31 x 48 grids
t_span = 264

df_conv = df_gt["weighted_combats"].as_matrix()
df_terr = df_gt["weighted_terrorism"].as_matrix()

xc = df_conv.reshape((t_span,r_span))
xt = df_terr.reshape((t_span,r_span))


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
	likelihood -= tf.reduce_sum(1 * tf.square(tf.subtract(tf.slice(z, [t, 0], [1, r_span-30]), tf.slice(z, [t, 30], [1, r_span-30]))))
	likelihood -= tf.reduce_sum(1 * tf.square(tf.subtract(tf.slice(z, [t, 0], [1, r_span-31]), tf.slice(z, [t, 31], [1, r_span-31]))))
	likelihood -= tf.reduce_sum(1 * tf.square(tf.subtract(tf.slice(z, [t, 0], [1, r_span-62]), tf.slice(z, [t, 62], [1, r_span-62]))))

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
    for step in range(20000):
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
