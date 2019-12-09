import { PipeTransform, Pipe } from '@angular/core';

@Pipe({ name: 'highlight' })

export class HighlightPipe implements PipeTransform {
    transform(text: any, search): string {
        let pattern = search.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, '\\$&');
        pattern = pattern.split(' ').filter((t) => {
            return t.length > 0;
        }).join('|');
        const regex = new RegExp(pattern, 'gi');

    return search ? text.replace(regex, (match) => `<span class="bg-warning">${match}</span>`) : text;
    }
}
