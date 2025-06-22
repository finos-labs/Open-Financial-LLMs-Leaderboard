import { useState, useCallback, useTransition } from 'react';

export const useBatchedState = (initialState, options = {}) => {
  const { batchDelay = 0, useTransitions = false } = options;
  const [state, setState] = useState(typeof initialState === 'function' ? initialState() : initialState);
  const [isPending, startTransition] = useTransition();

  const setBatchedState = useCallback((newState) => {
    if (useTransitions) {
      startTransition(() => {
        if (batchDelay > 0) {
          setTimeout(() => {
            setState(newState);
          }, batchDelay);
        } else {
          setState(newState);
        }
      });
    } else {
      if (batchDelay > 0) {
        setTimeout(() => {
          setState(newState);
        }, batchDelay);
      } else {
        setState(newState);
      }
    }
  }, [batchDelay, useTransitions]);

  return [state, setBatchedState, isPending];
}; 