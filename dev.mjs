import {spawn} from 'node:child_process';
import {existsSync} from 'node:fs';
const args=process.argv.slice(2),idx=args.indexOf('--port');
const port=idx>=0?args[idx+1]:'3000';
const runtime='/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python';
const python=existsSync(runtime)?runtime:(process.env.CODEX_PRIMARY_RUNTIME_PYTHON||'python3');
const child=spawn(python,['-m','uvicorn','app:app','--host','0.0.0.0','--port',port,'--no-access-log'],{stdio:'inherit',env:{...process.env,PREVIEW_MODE:'true',HOME:process.env.HOME||'/root'}});
child.on('exit',code=>process.exit(code??1));for(const signal of ['SIGTERM','SIGINT'])process.on(signal,()=>child.kill(signal));
