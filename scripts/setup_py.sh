export python_dir=python_env


if [ "$(uname)" == "Darwin" ]; then
    export python_exe=python_env/bin/python3   
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    export python_exe=python_env/Scripts/python.exe
fi

source ~/.bashrc

if [ ! -d $python_dir ]; then
    echo Creating python environment
    python3 -m venv $python_dir
    $python_exe -m pip install -r requirements.txt
fi

