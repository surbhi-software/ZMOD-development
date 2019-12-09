import { Pipe, PipeTransform } from '@angular/core';
import cronstrue from 'cronstrue';
@Pipe({
  name: 'cronstrue'
})
export class CronstruePipe implements PipeTransform {

  transform(value: any, args?: any): any {
    return cronstrue.toString(value);
  }

}
