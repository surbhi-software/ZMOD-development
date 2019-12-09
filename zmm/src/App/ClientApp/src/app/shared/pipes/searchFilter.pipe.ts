import { Injectable, Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'searchfilter'
})

@Injectable()
export class SearchFilterPipe implements PipeTransform {
    transform(items: any[], field: string, value: string): any[] {
        if (!items) { return []; }
        value = value.toLocaleLowerCase();
        return items.filter(it => {
            const name = it[field].toLocaleLowerCase();
            if (name.includes(value)) {
                return true;
            }
        });
    }
}
