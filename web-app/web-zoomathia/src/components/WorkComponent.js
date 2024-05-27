import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

const Work = () => {
    const [searchParams] = useSearchParams();

    const uri = searchParams.get('uri');

    return <div>
        <h1>Work page to directly display text</h1>
        <p>{uri}</p>
    </div >
}

export default Work;