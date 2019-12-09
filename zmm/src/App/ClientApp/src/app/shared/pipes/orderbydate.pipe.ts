import { Pipe, PipeTransform, Injectable } from '@angular/core';

@Pipe({
  name: 'orderByDate'
})

@Injectable()
export class OrderByDatePipe implements PipeTransform {
    transform(array: Array<any>, args: string): Array<any> {
        if (typeof args[0] === 'undefined') {
            return array;
        }
        const column = args.replace('-', '');
        array.sort((a: any, b: any) => {
            const left = Number(new Date(a[column]));
            const right = Number(new Date(b[column]));
            return (right - left);
        });
        return array;
    }
}
