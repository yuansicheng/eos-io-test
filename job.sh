#!/bin/bash

#source environment
echo sorsing environment...

export EOS_MGM_URL="root://junoeos01.ihep.ac.cn"
export EOS_HOME="/eos/juno/user/yuansc"
EOS_TEST_LUSTRE="/junofs/users/yuansc/eos-test/chain-test-lustre-20200915"
EOS_TEST_EOS="root://junoeos01.ihep.ac.cn//eos/juno/user/yuansc/chain-test-eos-20200915"
#EOS_TEST_EOS="root://junoeos01.ihep.ac.cn//eos/juno/user/yuansc/"

source /junofs/users/yuansc/juno-dev/bashrc

TMP_DIR="/tmp/yuansc"

if [ ! -d $TMP_DIR ] ; then
	mkdir $TMP_DIR
fi
cd $TMP_DIR

TIME_STAMP=PY_TIMESTAMP
MOMENTUMS=PY_MOMENTUMS
EVTMAX=PY_EVTMAX
NODE=PY_NODE

echo TIME_STAMP=$TIME_STAMP
echo EVTMAX=$EVTMAX
echo MOMENTUMS=$MOMENTUMS

THIS_DIR="/junofs/users/yuansc/eos-test/20201010/data/$TIME_STAMP"

#file path
TMP_DETSIM_OUTPUT=$TMP_DIR/sample_detsim_tmp_$TIME_STAMP.root
TMP_DETSIM_USER_OUTPUT=$TMP_DIR/sample_detsim_user_tmp_$TIME_STAMP.root
TMP_DETSIM_DCS_OUTPUT=$TMP_DIR/sample_detsim_dcs_tmp_$TIME_STAMP.root

TMP_ELECSIM_INPUT=$TMP_DETSIM_OUTPUT
TMP_ELECSIM_OUTPUT=$TMP_DIR/sample_elecsim_tmp_$TIME_STAMP.root
TMP_ELECSIM_USER_OUTPUT=$TMP_DIR/sample_elecsim_user_tmp_$TIME_STAMP.root
TMP_ELECSIM_DCS_OUTPUT=$TMP_DIR/sample_elecsim_dcs_tmp_$TIME_STAMP.root

LUSTRE_DETSIM_OUTPUT=$EOS_TEST_LUSTRE/sample_detsim_lustre_$TIME_STAMP.root
LUSTRE_DETSIM_USER_OUTPUT=$TMP_DIR/sample_detsim_user_lustre_$TIME_STAMP.root
LUSTRE_DETSIM_DCS_OUTPUT=$TMP_DIR/sample_detsim_dcs_lustre_$TIME_STAMP.root

LUSTRE_ELECSIM_INPUT=$LUSTRE_DETSIM_OUTPUT
LUSTRE_ELECSIM_OUTPUT=$EOS_TEST_LUSTRE/sample_elecsim_lustre_$TIME_STAMP.root
LUSTRE_ELECSIM_USER_OUTPUT=$TMP_DIR/sample_elecsim_user_lustre_$TIME_STAMP.root
LUSTRE_ELECSIM_DCS_OUTPUT=$TMP_DIR/sample_elecsim_dcs_lustre_$TIME_STAMP.root

EOS_DETSIM_OUTPUT=$EOS_TEST_EOS/sample_detsim_eos_$TIME_STAMP.root
EOS_DETSIM_USER_OUTPUT=$TMP_DIR/sample_detsim_user_eos_$TIME_STAMP.root
EOS_DETSIM_DCS_OUTPUT=$TMP_DIR/sample_detsim_dcs_eos_$TIME_STAMP.root

EOS_ELECSIM_INPUT=$EOS_DETSIM_OUTPUT
EOS_ELECSIM_OUTPUT=$EOS_TEST_EOS/sample_elecsim_eos_$TIME_STAMP.root
EOS_ELECSIM_USER_OUTPUT=$TMP_DIR/sample_elecsim_user_eos_$TIME_STAMP.root
EOS_ELECSIM_DCS_OUTPUT=$TMP_DIR/sample_elecsim_dcs_eos_$TIME_STAMP.root


#running detsim and elecsim

#tmp
python /junofs/users/yuansc/juno-dev/offline/Examples/Tutorial/share/tut_detsim.py \
	--evtmax $EVTMAX \
	--output $TMP_DETSIM_OUTPUT \
	--dcs-output sample_detsim_dcs_tmp_$TIME_STAMP.root \
	--user-output sample_detsim_user_tmp_$TIME_STAMP.root \
	gun \
	--momentums $MOMENTUMS

python /junofs/users/yuansc/juno-dev/offline/Examples/Tutorial/share/tut_det2elec.py \
	--evtmax $EVTMAX \
	--input $TMP_ELECSIM_INPUT \
	--output $TMP_ELECSIM_OUTPUT \
	--user-output $TMP_ELECSIM_USER_OUTPUT \
	--dcs-output $TMP_ELECSIM_DCS_OUTPUT

#lustre

python /junofs/users/yuansc/juno-dev/offline/Examples/Tutorial/share/tut_detsim.py \
	--evtmax $EVTMAX \
	--output $LUSTRE_DETSIM_OUTPUT \
	--dcs-output $LUSTRE_DETSIM_DCS_OUTPUT \
	--user-output $LUSTRE_DETSIM_USER_OUTPUT \
	gun \
	--momentums $MOMENTUMS

python /junofs/users/yuansc/juno-dev/offline/Examples/Tutorial/share/tut_det2elec.py \
	--evtmax $EVTMAX \
	--input $LUSTRE_ELECSIM_INPUT \
	--output $LUSTRE_ELECSIM_OUTPUT \
	--user-output $LUSTRE_ELECSIM_USER_OUTPUT \
	--dcs-output $LUSTRE_ELECSIM_DCS_OUTPUT

#eos

python /junofs/users/yuansc/juno-dev/offline/Examples/Tutorial/share/tut_detsim.py \
	--evtmax $EVTMAX \
	--output $EOS_DETSIM_OUTPUT \
	--dcs-output $EOS_DETSIM_DCS_OUTPUT \
	--user-output $EOS_DETSIM_USER_OUTPUT \
	gun \
	--momentums $MOMENTUMS

python /junofs/users/yuansc/juno-dev/offline/Examples/Tutorial/share/tut_det2elec.py \
	--evtmax $EVTMAX \
	--input default:$EOS_ELECSIM_INPUT \
	--output $EOS_ELECSIM_OUTPUT \
	--user-output $EOS_ELECSIM_USER_OUTPUT \
	--dcs-output $EOS_ELECSIM_DCS_OUTPUT

echo removing files...

#tmp
rm $TMP_DETSIM_OUTPUT
rm $TMP_DETSIM_USER_OUTPUT
rm $TMP_ELECSIM_OUTPUT
rm $TMP_ELECSIM_USER_OUTPUT
cp $TMP_DETSIM_DCS_OUTPUT $THIS_DIR
cp $TMP_ELECSIM_DCS_OUTPUT $THIS_DIR

#luntre
rm $LUSTRE_DETSIM_OUTPUT
rm $LUSTRE_DETSIM_USER_OUTPUT
rm $LUSTRE_ELECSIM_OUTPUT
rm $LUSTRE_ELECSIM_USER_OUTPUT
cp $LUSTRE_DETSIM_DCS_OUTPUT $THIS_DIR
cp $LUSTRE_ELECSIM_DCS_OUTPUT $THIS_DIR

#eos
eos rm $EOS_DETSIM_OUTPUT
rm $EOS_DETSIM_USER_OUTPUT
eos rm $EOS_ELECSIM_OUTPUT
rm $EOS_ELECSIM_USER_OUTPUT
cp $EOS_DETSIM_DCS_OUTPUT $THIS_DIR
cp $EOS_ELECSIM_DCS_OUTPUT $THIS_DIR













