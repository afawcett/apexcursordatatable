import ApexCursorDemo from 'c/apexCursorDemo';
import { createElement } from '@lwc/engine-dom';

describe('c-apex-cursor-demo', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('renders the component', () => {
        const element = createElement('c-apex-cursor-demo', {
            is: ApexCursorDemo
        });

        document.body.appendChild(element);

        expect(element).toBeTruthy();
    });
});
